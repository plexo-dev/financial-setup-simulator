import pandas as pd


def process_data(df):
    df["sma20"] = df["Close"].rolling(window=20).mean()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    if price < df["sma20"].iloc[-1]:
        if price > (portfolio["price_bought"] * (1 + comission)):
            return True
    return False


def check_buying_conditions(df, price, portfolio):
    if price > df["sma20"].iloc[-1]:
        if price < portfolio["price_sold"] * 0.95 or price > portfolio["price_sold"] * 1.15:
            return True
    return False
