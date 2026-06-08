from utis import get_amount

IBOVESPA_SYMBOL = "^BVSP"
USD_BRL_SYMBOL = "USDBRL=X"


def buy_and_hold_metrics(df, initial_balance):
    """Buy at first close in the fetched window; hold to last close."""
    if df.empty:
        return {
            "buy_hold_total_value": initial_balance,
            "buy_hold_gain_amount": 0.0,
            "buy_hold_return_pct": 0.0,
            "buy_hold_shares": 0,
            "buy_hold_entry_price": 0.0,
            "buy_hold_exit_price": 0.0,
        }

    entry_price = float(df["Close"].iloc[0])
    exit_price = float(df["Close"].iloc[-1])
    shares = get_amount(1.0, initial_balance, entry_price)
    spent = shares * entry_price
    total_value = shares * exit_price + (initial_balance - spent)
    gain_amount = total_value - initial_balance
    return_pct = (gain_amount / initial_balance) * 100 if initial_balance else 0

    return {
        "buy_hold_total_value": total_value,
        "buy_hold_gain_amount": gain_amount,
        "buy_hold_return_pct": return_pct,
        "buy_hold_shares": shares,
        "buy_hold_entry_price": entry_price,
        "buy_hold_exit_price": exit_price,
    }


def _indexed_series(df):
    if df.empty:
        return []
    base = float(df["Close"].iloc[0])
    return [
        {"date": idx.isoformat(), "index": (float(row["Close"]) / base) * 100}
        for idx, row in df.iterrows()
    ]


def period_return_metrics(df, initial_balance):
    """Percentage move over the window (for indices and FX rates)."""
    if df.empty:
        return {
            "buy_hold_total_value": initial_balance,
            "buy_hold_gain_amount": 0.0,
            "buy_hold_return_pct": 0.0,
            "buy_hold_shares": 0,
            "buy_hold_entry_price": 0.0,
            "buy_hold_exit_price": 0.0,
        }

    entry_price = float(df["Close"].iloc[0])
    exit_price = float(df["Close"].iloc[-1])
    return_pct = ((exit_price / entry_price) - 1) * 100 if entry_price else 0
    gain_amount = initial_balance * (return_pct / 100)
    total_value = initial_balance + gain_amount

    return {
        "buy_hold_total_value": total_value,
        "buy_hold_gain_amount": gain_amount,
        "buy_hold_return_pct": return_pct,
        "buy_hold_shares": 0,
        "buy_hold_entry_price": entry_price,
        "buy_hold_exit_price": exit_price,
    }


def _rate_benchmark(name, symbol, period, interval, initial_balance):
    import yfinance as yf

    df = yf.Ticker(symbol).history(period, interval)
    metrics = period_return_metrics(df, initial_balance)
    return {
        "name": name,
        "symbol": symbol,
        "period": period,
        "interval": interval,
        **metrics,
        "normalized_series": _indexed_series(df),
    }


def ibovespa_benchmark(period, interval, initial_balance):
    return _rate_benchmark("Ibovespa", IBOVESPA_SYMBOL, period, interval, initial_balance)


def dollar_benchmark(period, interval, initial_balance):
    """USD/BRL move over the period (BRL per USD; up = dollar strengthening)."""
    return _rate_benchmark("USD/BRL", USD_BRL_SYMBOL, period, interval, initial_balance)
