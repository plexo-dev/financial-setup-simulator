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
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi14"] = 100 - (100 / (1 + rs))
    df["sma50"] = df["Close"].rolling(window=50).mean()
    df["sma50_slope"] = df["sma50"].diff(5)
    df["sma20"] = df["Close"].rolling(window=20).mean()
    df["std20"] = df["Close"].rolling(window=20).std()
    df["bb_upper"] = df["sma20"] + 2 * df["std20"]
    df["atr14"] = _atr(df)
    df["high10"] = df["High"].rolling(window=10).max()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    if price < entry - 2.5 * atr:
        return True
    if price >= df["bb_upper"].iloc[-1]:
        return True
    trail = df["high10"].iloc[-1] - 2.0 * atr
    if price < trail:
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    rsi = df["rsi14"].iloc[-1]
    y = portfolio.get("_entry_reluctance", 1.0)
    rsi_limit = 38 - max(0.0, y - 1.0) * 8
    if rsi > rsi_limit:
        return reluctant_entry(False, portfolio)
    if price < df["sma50"].iloc[-1]:
        return reluctant_entry(False, portfolio)
    if df["sma50_slope"].iloc[-1] <= 0:
        return reluctant_entry(False, portfolio)
    sold = portfolio["price_sold"]
    if sold != float("inf") and sold * 0.97 < price < sold * 1.04:
        return reluctant_entry(False, portfolio)
    return reluctant_entry(True, portfolio)
