import pandas as pd


def process_data(df):
    df["sma8"] = df["Close"].rolling(window=8).mean()
    df["sma21"] = df["Close"].rolling(window=21).mean()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    if df["sma8"].iloc[-1] < df["sma21"].iloc[-1]:
        if price > (portfolio["price_bought"] * (1 + comission)):
            return True
    return False


def check_buying_conditions(df, price, portfolio):
    if df["sma8"].iloc[-1] > df["sma21"].iloc[-1]:
        if price < portfolio["price_sold"] * 0.98 or price > portfolio["price_sold"] * 1.05:
            return True
    return False
