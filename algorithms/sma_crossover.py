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
    df["sma8"] = df["Close"].rolling(window=8).mean()
    df["sma21"] = df["Close"].rolling(window=21).mean()
    df["sma50"] = df["Close"].rolling(window=50).mean()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi14"] = 100 - (100 / (1 + rs))
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
    if df["sma8"].iloc[-1] < df["sma21"].iloc[-1]:
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    if len(df) < 2:
        return reluctant_entry(False, portfolio)
    if price < df["sma50"].iloc[-1]:
        return reluctant_entry(False, portfolio)
    if df["sma8"].iloc[-1] <= df["sma21"].iloc[-1]:
        return reluctant_entry(False, portfolio)
    if df["sma8"].iloc[-2] > df["sma21"].iloc[-2]:
        return reluctant_entry(False, portfolio)
    if df["rsi14"].iloc[-1] > 65:
        return reluctant_entry(False, portfolio)
    return reluctant_entry(True, portfolio)
