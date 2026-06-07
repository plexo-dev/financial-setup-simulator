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
    df["high20"] = df["High"].rolling(window=20).max().shift(1)
    df["low20"] = df["Low"].rolling(window=20).min().shift(1)
    df["sma50"] = df["Close"].rolling(window=50).mean()
    df["std20"] = df["Close"].rolling(window=20).std()
    df["bb_width"] = (df["std20"] * 4) / df["sma50"]
    df["bb_width_ma"] = df["bb_width"].rolling(100).mean()
    df["atr14"] = _atr(df)
    df["high22"] = df["High"].rolling(window=22).max()
    if "Volume" in df.columns:
        df["vol_avg20"] = df["Volume"].rolling(window=20).mean()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    if price < entry - 2.5 * atr:
        return True
    trail = df["high22"].iloc[-1] - 2.5 * atr
    if price < trail:
        return True
    if price < df["low20"].iloc[-1]:
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    high20 = df["high20"].iloc[-1]
    if price <= high20 * 1.002:
        return reluctant_entry(False, portfolio)
    if price < df["sma50"].iloc[-1]:
        return reluctant_entry(False, portfolio)
    if df["bb_width"].iloc[-1] > df["bb_width_ma"].iloc[-1]:
        return reluctant_entry(False, portfolio)
    y = portfolio.get("_entry_reluctance", 1.0)
    vol_mult = 1.1 + max(0.0, y - 1.0) * 0.1
    if "vol_avg20" in df.columns and df["Volume"].iloc[-1] < df["vol_avg20"].iloc[-1] * vol_mult:
        return reluctant_entry(False, portfolio)
    sold = portfolio["price_sold"]
    if sold != float("inf") and sold * 0.97 < price < sold * 1.04:
        return reluctant_entry(False, portfolio)
    return reluctant_entry(True, portfolio)
