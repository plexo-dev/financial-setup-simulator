import pandas as pd
from algorithm_helpers import entry_gate, entry_filters_active, first_sell_reason


def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(window).mean()


def process_data(df):
    df["sma20"] = df["Close"].rolling(window=20).mean()
    df["sma50"] = df["Close"].rolling(window=50).mean()
    df["sma20_slope"] = df["sma20"].diff(2)
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
        ("SMA-50 break", price < df["sma50"].iloc[-1]),
    ], portfolio)
    if reason:
        portfolio["_last_exit_reason"] = reason
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    sma20 = df["sma20"].iloc[-1]
    sma50 = df["sma50"].iloc[-1]
    if price <= sma20 or df["sma20_slope"].iloc[-1] <= 0:
        return entry_gate(False, portfolio)
    if sma20 < sma50:
        return entry_gate(False, portfolio)
    if entry_filters_active(portfolio):
        if price < sma50 * 0.98 or price > sma50 * 1.04:
            return entry_gate(False, portfolio)
        if price > sma20 * 1.04:
            return entry_gate(False, portfolio)
        sold = portfolio["price_sold"]
        if sold != float("inf") and sold * 0.94 < price < sold * 1.06:
            return entry_gate(False, portfolio)
    return entry_gate(True, portfolio)
