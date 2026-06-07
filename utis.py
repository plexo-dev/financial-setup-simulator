import re

import yfinance as yf
import plotly.graph_objects as go

B3_TICKER_PATTERN = re.compile(r"^[A-Z]{4}\d{1,2}\.SA$")

# Common liquid B3 tickers (Yahoo Finance uses the .SA suffix).
B3_SYMBOLS = (
    "PETR4.SA",
    "VALE3.SA",
    "ITUB4.SA",
    "BBDC4.SA",
    "ABEV3.SA",
    "WEGE3.SA",
    "BBAS3.SA",
    "RENT3.SA",
    "B3SA3.SA",
    "SUZB3.SA",
)


def normalize_b3_symbol(symbol):
    symbol = str(symbol).strip().upper()
    if not symbol.endswith(".SA"):
        symbol = f"{symbol}.SA"
    return symbol


def is_b3_symbol(symbol):
    return bool(B3_TICKER_PATTERN.fullmatch(symbol))


def validate_b3_symbol(symbol):
    normalized = normalize_b3_symbol(symbol)
    if not is_b3_symbol(normalized):
        raise ValueError(
            "Only B3 (Bovespa) stocks are supported. "
            "Use a ticker like PETR4.SA or VALE3.SA."
        )
    return normalized


# get_stocks(symbol)
def get_stocks(symbol, period, interval):
    """_summary_

    Args:
        symbol (_str_): _stock symbol to be fetched_
        period (_str_): _period to be fetched_
        interval (_str_): _interval to be fetched_

    Returns:
        _<pandas.core.frame.DataFrame_: _Historical data and selected indicators pandas DataFrame_
    """

    symbol = validate_b3_symbol(symbol)

    # Fetch data
    ticker = yf.Ticker(symbol)
    df = ticker.history(period, interval)

    return df


# buy(portfolio_dictionary, amount)
def buy(portfolio, price, amount):
    """_summary_

    Args:
        portfolio (_dict_): _{"amount" : int, "balance" : float, "price_bought" : float}_
        price (_float_): _price to be bought_
        amount (_type_): _shares ammount to be bought_

    Returns:
        _dict_: _atualized portfolio_
    """
    # Error handling
    if portfolio["balance"] < price * amount:
        return portfolio

    # Atualizing portfolio
    portfolio["amount"] += amount
    portfolio["balance"] -= price * amount
    portfolio["price_bought"] = price

    return portfolio

# sell(portfolio_dictionary, amount=max)
def sell(portfolio, comission, price, amount=-1,): # -1 for amount = maximum
    """_summary_

    Args:
        portfolio (_dict_): _{"amount" : int, "balance" : float, "price_sold" : float}_
        comission (_float_): _broker's commission to be discounted (0.value)_
        price (_float_): _price to be sold_
        amount (int, optional): _ammount to be sold_. Defaults to max.

    Returns:
        _dict_: _atualized portfolio_
    """

    # Get amount before function
    old_amount = portfolio["amount"]

    # Error handling
    if old_amount < amount:
        return portfolio

    # For selling all stocks
    if amount == -1:
        portfolio["amount"] = 0
        portfolio["balance"] += price * old_amount * (1 - comission)
        portfolio["price_sold"] = price

    # For selling specific amount
    else:
        portfolio["amount"] -= amount
        portfolio["balance"] += price *  amount * (1 - comission)

    return portfolio

def get_amount(lot_size, balance, price):


    amount = lot_size * balance / price
    amount = int(amount - amount % 1)
    if amount == 0:
        amount = 1

    return amount


def get_stock_name(symbol):
    symbol = validate_b3_symbol(symbol)
    ticker = yf.Ticker(symbol)
    name = ticker.info["longName"]
    return name
