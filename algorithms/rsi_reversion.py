import pandas as pd


def process_data(df):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi14"] = 100 - (100 / (1 + rs))
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    if df["rsi14"].iloc[-1] > 65:
        if price > (portfolio["price_bought"] * (1 + comission)):
            return True
    return False


def check_buying_conditions(df, price, portfolio):
    if df["rsi14"].iloc[-1] < 35:
        return True
    return False
