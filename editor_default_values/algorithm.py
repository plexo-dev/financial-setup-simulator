# Algorythm for trend following using moving averages of 8 candles
import pandas as pd


def process_data(df):
    """_preprocess data from a pandas dataframe for financial analysis_

    Args:
        df (_pandas.core.frame.DataFrame_): _{"Open": _float64_, "High": _float64_, "Low": _float64_, "Close": _float64_, "Volume": _int64_, "Dividends": _float64_, "Stock Splits": _float64_, }_

    Returns:
        _pandas.core.frame.DataFrame_: _Same df but with added columns_
    """

    # Fetch moving averages.

    Moving_averages = [8]  # Moving averages to be calculed.
    for i in Moving_averages:
        df[f"sma{i}"] = df["Close"].rolling(window=i).mean()  # Calcules moving averages.
    # Drop empty cells.
    df = df.dropna()

    return df


def check_selling_conditions(df, price, portfolio, comission):
    """_returns wether the stocks sould be selled(True) or not(False)_

    Args:
        df (_pandas.core.frame.DataFrame_): _Pandas Data frame with fetched financial data_
        price (_float64_): _df["Close"].iloc[-1]_
        portfolio (_dict_): _{"amount" : _int_, "price_bought" : _float64_, "balance" : _float64_, "symbol" : _str_, "stoploss" : _numpy.float64_, "takeprofit" : _numpy.float64_}_
        comission (_float_): _The commission payed into the sells_

    Returns:
        _bool_: _returns wether the stocks sould be selled(True) or not(False)_
    """

    # Checks if the price is smaller than the moving average of 8 candles.
    # Signs a downtrend. Algorythm will try to leave operation.
    if price < df["sma8"].iloc[-1]:
        # Check if sell gives profit.
        if price > (portfolio["price_bought"] * (1 + comission)):
            # Sell stocks.
            return True
    # Don't sell stocks.
    return False


def check_buying_conditions(df, price, portfolio):
    """_returns wether the stocks sould be bought(True) or not(False)_

    Args:
        df (_pandas.core.frame.DataFrame_): _Pandas Data frame with fetched financial data_
        price (_float64_): _df["Close"].iloc[-1]_
        portfolio (_dict_): _{"amount" : _int_, "price_bought" : _float64_, "balance" : _float64_, "symbol" : _str_, "stoploss" : _numpy.float64_, "takeprofit" : _numpy.float64_}_

    Returns:
        _bool_: _returns wether the stocks sould be bought(True) or not(False)_
    """
    # Adjust the volatility for your time frame and stock
    volatility = 1

    # Checks if there is a uptrend (price is higher than moving average of 8 candles).
    if price > df["sma8"].iloc[-1]:
        # Check if previous sell won't be overriden or if the stocks went straight up
        if price < (portfolio["price_sold"] * (1 - 0.1 * volatility)) or price > (portfolio["price_sold"] * (1 + 0.2 * volatility)):
            # Buy stocks.
            return True

    # Don't buy stocks
    return False
