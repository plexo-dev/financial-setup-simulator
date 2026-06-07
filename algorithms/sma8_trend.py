import pandas as pd


def process_data(df):
    df["sma8"] = df["Close"].rolling(window=8).mean()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    if price < df["sma8"].iloc[-1]:
        if price > (portfolio["price_bought"] * (1 + comission)):
            return True
    return False


def check_buying_conditions(df, price, portfolio):
    volatility = 1
    if price > df["sma8"].iloc[-1]:
        if price < (portfolio["price_sold"] * (1 - 0.1 * volatility)) or price > (
            portfolio["price_sold"] * (1 + 0.2 * volatility)
        ):
            return True
    return False
