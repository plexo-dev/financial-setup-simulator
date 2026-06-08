# RSI pullback in uptrend + TA-Lib bullish reversal candle confirmation
import pandas as pd
from algorithm_helpers import entry_gate, entry_filters_active, first_sell_reason, add_bullish_reversal_column


def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / window, adjust=False).mean()


def _has_bullish_reversal(df):
    if df["bullish_reversal"].iloc[-1]:
        return True
    if len(df) >= 2 and df["bullish_reversal"].iloc[-2]:
        return True
    return False


def process_data(df):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi14"] = 100 - (100 / (1 + rs))
    df["sma21"] = df["Close"].rolling(window=21).mean()
    df["sma50"] = df["Close"].rolling(window=50).mean()
    df["sma50_slope"] = df["sma50"].diff(5)
    df["sma20"] = df["Close"].rolling(window=20).mean()
    df["std20"] = df["Close"].rolling(window=20).std()
    df["bb_upper"] = df["sma20"] + 2 * df["std20"]
    df["atr14"] = _atr(df)
    df["high22"] = df["High"].rolling(window=22).max()
    add_bullish_reversal_column(df)
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    rsi = df["rsi14"].iloc[-1]
    sma21 = df["sma21"].iloc[-1]
    bb_upper = df["bb_upper"].iloc[-1]
    stop_mult = 2.0 if price < sma21 else 2.5
    trail = df["high22"].iloc[-1] - 2.5 * atr
    reason = first_sell_reason([
        ("ATR stop", price < entry - stop_mult * atr),
        ("Chandelier trail", price < trail),
        ("Bollinger take profit", price >= bb_upper and rsi > 62),
        ("RSI overbought", rsi > 72),
    ], portfolio)
    if reason:
        portfolio["_last_exit_reason"] = reason
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    rsi = df["rsi14"].iloc[-1]
    rsi_limit = 40
    if entry_filters_active(portfolio):
        y = portfolio.get("_entry_reluctance", 1.0)
        rsi_limit = 40 - max(0.0, y - 1.0) * 7
    if rsi > rsi_limit:
        return entry_gate(False, portfolio)
    if price < df["sma50"].iloc[-1]:
        return entry_gate(False, portfolio)
    if df["sma50_slope"].iloc[-1] <= 0:
        return entry_gate(False, portfolio)
    if entry_filters_active(portfolio):
        if not _has_bullish_reversal(df) and rsi >= 32:
            return entry_gate(False, portfolio)
        sold = portfolio["price_sold"]
        if sold != float("inf"):
            if price > sold * 1.03:
                return entry_gate(False, portfolio)
            if sold * 0.96 < price < sold * 1.05:
                return entry_gate(False, portfolio)
    return entry_gate(True, portfolio)
