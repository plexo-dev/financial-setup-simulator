import pandas as pd
from algorithm_helpers import reluctant_entry


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
    df["sma20_slope"] = df["sma20"].diff(5)
    df["atr14"] = _atr(df)
    df["high22"] = df["High"].rolling(window=22).max()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    if price < entry - 3.0 * atr:
        return True
    trail = df["high22"].iloc[-1] - 2.5 * atr
    if price < trail:
        return True
    if price < df["sma50"].iloc[-1]:
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    sma20 = df["sma20"].iloc[-1]
    sma50 = df["sma50"].iloc[-1]
    if price <= sma20 or df["sma20_slope"].iloc[-1] <= 0:
        return reluctant_entry(False, portfolio)
    if price < sma50 * 0.995:
        return reluctant_entry(False, portfolio)
    if price > sma50 * 1.03:
        return reluctant_entry(False, portfolio)
    if sma20 < sma50:
        return reluctant_entry(False, portfolio)
    if price > sma20 * 1.04:
        return reluctant_entry(False, portfolio)
    sold = portfolio["price_sold"]
    if sold != float("inf") and sold * 0.96 < price < sold * 1.06:
        return reluctant_entry(False, portfolio)
    return reluctant_entry(True, portfolio)
