from utis import get_stocks, buy, sell, get_amount, get_stock_name


def run_backtest(
    symbol,
    period,
    interval,
    algorithm_source,
    initial_balance=10000.0,
    lot_size_pct=75,
    commission_pct=1,
    initial_stocks=0,
):
    user_functions = {}
    exec(algorithm_source, user_functions)

    lot_size = lot_size_pct / 100
    commission = commission_pct / 100
    output = []
    portfolio = {
        "amount": initial_stocks,
        "price_bought": 0,
        "price_sold": float("inf"),
        "date_bought": 0,
        "balance": initial_balance,
        "symbol": symbol.upper(),
    }

    full_df = get_stocks(symbol.upper(), period, interval)
    full_df = user_functions["process_data"](full_df)
    df = full_df.iloc[:0].copy()

    buys = 0
    sells = 0
    price = 0.0

    for index, row in full_df.iterrows():
        df.loc[index] = row
        price = float(row["Close"])
        amount = get_amount(lot_size, portfolio["balance"], price)

        if portfolio["amount"]:
            if user_functions["check_selling_conditions"](df, price, portfolio, commission):
                portfolio = sell(portfolio, commission, price)
                sells += 1
                output.append(
                    {"Action": "Sell", "Message": f"Sold at {price:.2f}; balance: {portfolio['balance']:.2f}"}
                )
        elif user_functions["check_buying_conditions"](df, price, portfolio):
            portfolio = buy(portfolio, price, amount)
            buys += 1
            output.append(
                {"Action": "Buy", "Message": f"Bought at {price:.2f}; balance: {portfolio['balance']:.2f}"}
            )

    total_value = float(portfolio["balance"]) + float(portfolio["amount"] * price)
    gain_amount = total_value - initial_balance
    return_pct = (gain_amount / initial_balance) * 100 if initial_balance else 0

    return {
        "symbol": symbol.upper(),
        "name": get_stock_name(symbol.upper()),
        "period": period,
        "interval": interval,
        "initial_balance": initial_balance,
        "total_value": total_value,
        "gain_amount": gain_amount,
        "return_pct": return_pct,
        "trade_count": buys + sells,
        "buys": buys,
        "sells": sells,
        "output": output,
    }
