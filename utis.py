import yfinance as yf
import plotly.graph_objects as go


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

    # Fetch data
    ticker = yf.Ticker(symbol.upper())
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
    ticker = yf.Ticker(symbol.upper())
    name = ticker.info["longName"]
    return name
