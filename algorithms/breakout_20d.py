import pandas as pd


def process_data(df):
    df["high20"] = df["High"].rolling(window=20).max().shift(1)
    df["low20"] = df["Low"].rolling(window=20).min().shift(1)
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    if price < df["low20"].iloc[-1]:
        if price > (portfolio["price_bought"] * (1 + comission)):
            return True
    return False


def check_buying_conditions(df, price, portfolio):
    if price > df["high20"].iloc[-1]:
        return True
    return False
