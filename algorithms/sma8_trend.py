import pandas as pd
from algorithm_helpers import entry_gate, entry_filters_active, first_sell_reason


def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / window, adjust=False).mean()


def process_data(df):
    df["sma8"] = df["Close"].rolling(window=8).mean()
    df["sma21"] = df["Close"].rolling(window=21).mean()
    df["sma50"] = df["Close"].rolling(window=50).mean()
    df["sma8_slope"] = df["sma8"].diff(2)
    df["atr14"] = _atr(df)
    df["high22"] = df["High"].rolling(window=22).max()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    trail = df["high22"].iloc[-1] - 2.5 * atr
    reason = first_sell_reason([
        ("ATR stop", price < entry - 30.0 * atr),
        ("Chandelier trail", price < trail),
        ("SMA break", price < df["sma21"].iloc[-1]),
    ], portfolio)
    if reason:
        portfolio["_last_exit_reason"] = reason
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    sma8 = df["sma8"].iloc[-1]
    if price <= sma8 or df["sma8_slope"].iloc[-1] <= 0:
        return entry_gate(False, portfolio)
    if price < df["sma21"].iloc[-1] or price < df["sma50"].iloc[-1]:
        return entry_gate(False, portfolio)
    if entry_filters_active(portfolio):
        y = portfolio.get("_entry_reluctance", 1.0)
        ext_limit = 1.035 - max(0.0, y - 1.0) * 0.008
        if price > sma8 * ext_limit:
            return entry_gate(False, portfolio)
        sold = portfolio["price_sold"]
        if sold != float("inf") and sold * 0.96 < price < sold * 1.05:
            return entry_gate(False, portfolio)
    return entry_gate(True, portfolio)
