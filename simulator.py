import json

import plotly
import plotly.graph_objects as go

from algorithm_helpers import exec_user_algorithm, update_time_state
from benchmarks import buy_and_hold_metrics
from risk_metrics import buy_hold_equity_series, compute_risk_metrics, regime_returns
from utis import get_stocks, buy, sell, get_amount, get_stock_name

GRAPH_IGNORE = ["Open", "Low", "High", "Close", "Dividends", "Stock Splits", "Volume"]


def final_position_label(portfolio, buys):
    """Bought = holding shares; Sold = flat cash after trading; Neutral = never entered."""
    if portfolio["amount"] > 0:
        return "Bought"
    if buys > 0:
        return "Sold"
    return "Neutral"


def _build_figure(full_df):
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=full_df.index,
                open=full_df["Open"].tolist(),
                high=full_df["High"].tolist(),
                low=full_df["Low"].tolist(),
                close=full_df["Close"].tolist(),
                name="Candlesticks",
            )
        ]
    )

    colors = ["yellow", "orange", "cyan", "purple", "blue"]
    for column in full_df:
        if column not in GRAPH_IGNORE:
            color = colors.pop() if colors else None
            fig.add_trace(
                go.Scatter(
                    x=full_df.index,
                    y=full_df[column].tolist(),
                    mode="lines",
                    name=column,
                    line=dict(color=color, width=1) if color else dict(width=2),
                )
            )

    fig.update_layout(xaxis_rangeslider_visible=False, height=360, margin=dict(t=40, b=40))
    fig.update_xaxes(type="date")
    return fig


def _regime_frame(full_df):
    frame = full_df.copy()
    if "sma50" not in frame.columns:
        frame["sma50"] = frame["Close"].rolling(window=50).mean()
    if "sma50_slope" not in frame.columns:
        frame["sma50_slope"] = frame["sma50"].diff(5)
    if "atr14" not in frame.columns:
        prev = frame["Close"].shift()
        tr = (frame["High"] - frame["Low"]).combine(
            (frame["High"] - prev).abs(), max
        ).combine((frame["Low"] - prev).abs(), max)
        frame["atr14"] = tr.rolling(window=14).mean()
    return frame


def run_backtest(
    symbol,
    period,
    interval,
    algorithm_source,
    initial_balance=10000.0,
    lot_size_pct=75,
    commission_pct=1,
    initial_stocks=0,
    include_graph=False,
    experiment_mode="full",
):
    user_functions = exec_user_algorithm(algorithm_source)

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
        "_experiment_mode": experiment_mode or "full",
    }

    raw_df = get_stocks(symbol.upper(), period, interval)
    period_start = raw_df.index[0].strftime("%Y-%m-%d") if len(raw_df) else None
    period_end = raw_df.index[-1].strftime("%Y-%m-%d") if len(raw_df) else None
    buy_hold = buy_and_hold_metrics(raw_df, initial_balance)
    full_df = user_functions["process_data"](raw_df)
    df = full_df.iloc[:0].copy()
    fig = _build_figure(full_df) if include_graph else None

    buys = 0
    sells = 0
    price = 0.0
    equity_series = []
    exit_attribution = {}
    round_trip_entry_equity = None
    bars_in_market = 0

    total_bars = len(full_df)
    for bar_index, (index, row) in enumerate(full_df.iterrows(), start=1):
        df.loc[index] = row
        update_time_state(portfolio, bar_index, total_bars)
        price = float(row["Close"])
        amount = get_amount(lot_size, portfolio["balance"], price)
        equity = float(portfolio["balance"]) + float(portfolio["amount"] * price)
        equity_series.append({"date": index.isoformat(), "equity": equity})
        if portfolio["amount"] > 0:
            bars_in_market += 1

        if portfolio["amount"]:
            if user_functions["check_selling_conditions"](df, price, portfolio, commission):
                entry_equity = round_trip_entry_equity if round_trip_entry_equity is not None else equity
                reason = portfolio.pop("_last_exit_reason", "Unknown exit")
                portfolio = sell(portfolio, commission, price)
                sells += 1
                sell_equity = float(portfolio["balance"])
                if entry_equity > 0:
                    pnl_pct = (sell_equity - entry_equity) / entry_equity * 100
                    exit_attribution[reason] = exit_attribution.get(reason, 0.0) + pnl_pct
                round_trip_entry_equity = None
                output.append(
                    {
                        "Action": "Sell",
                        "Message": f"Sold at {price:.2f} ({reason}); balance: {portfolio['balance']:.2f}",
                        "Reason": reason,
                    }
                )
                if fig is not None:
                    fig.add_trace(
                        go.Scatter(
                            x=[df.index[-1]],
                            y=[df["High"].iloc[-1] * 1.1],
                            mode="markers",
                            showlegend=False,
                            marker=dict(color="green", symbol="triangle-down", size=10),
                            text=f"Price sold: {price:.2f}",
                            hoverinfo="text",
                        )
                    )
        elif user_functions["check_buying_conditions"](df, price, portfolio):
            portfolio = buy(portfolio, price, amount)
            buys += 1
            round_trip_entry_equity = float(portfolio["balance"]) + float(portfolio["amount"] * price)
            output.append(
                {"Action": "Buy", "Message": f"Bought at {price:.2f}; balance: {portfolio['balance']:.2f}"}
            )
            if fig is not None:
                fig.add_trace(
                    go.Scatter(
                        x=[df.index[-1]],
                        y=[df["Low"].iloc[-1] * 0.9],
                        mode="markers",
                        showlegend=False,
                        marker=dict(color="red", symbol="triangle-up", size=10),
                        text=f"Price bought: {price:.2f}",
                        hoverinfo="text",
                    )
                )

    total_value = float(portfolio["balance"]) + float(portfolio["amount"] * price)
    gain_amount = total_value - initial_balance
    return_pct = (gain_amount / initial_balance) * 100 if initial_balance else 0

    final_position = final_position_label(portfolio, buys)
    vs_buy_hold = return_pct - buy_hold["buy_hold_return_pct"]

    benchmark_equity = buy_hold_equity_series(full_df, initial_balance)
    risk = compute_risk_metrics(equity_series, benchmark_equity, return_pct)
    regimes = regime_returns(equity_series, _regime_frame(full_df))
    exposure_pct = (bars_in_market / total_bars * 100) if total_bars else 0.0

    output.append(
        {
            "Action": "Summary",
            "Message": (
                f"Final position: {final_position} "
                f"({portfolio['amount']} shares, cash R$ {portfolio['balance']:.2f})"
            ),
        }
    )
    output.append(
        {
            "Action": "Summary",
            "Message": (
                f"Buy & hold: R$ {buy_hold['buy_hold_gain_amount']:.2f} "
                f"({buy_hold['buy_hold_return_pct']:.2f}%) · "
                f"Strategy vs buy & hold: {vs_buy_hold:+.2f} pp · "
                f"Max DD: {risk['max_drawdown_pct']:.1f}% vs {risk['buy_hold_max_drawdown_pct']:.1f}% · "
                f"Sharpe: {risk['sharpe']:.2f} vs {risk['buy_hold_sharpe']:.2f} · "
                f"Time in market: {exposure_pct:.1f}%"
            ),
        }
    )

    result = {
        "symbol": symbol.upper(),
        "name": get_stock_name(symbol.upper()),
        "period": period,
        "interval": interval,
        "period_start": period_start,
        "period_end": period_end,
        "initial_balance": initial_balance,
        "total_value": total_value,
        "gain_amount": gain_amount,
        "return_pct": return_pct,
        "trade_count": buys + sells,
        "buys": buys,
        "sells": sells,
        "final_shares": int(portfolio["amount"]),
        "final_balance": float(portfolio["balance"]),
        "final_position": final_position,
        "vs_buy_hold_pct": vs_buy_hold,
        "output": output,
        "equity_series": equity_series,
        "exit_attribution": exit_attribution,
        "regime_returns": regimes,
        "bars_in_market": bars_in_market,
        "total_bars": total_bars,
        "exposure_pct": round(exposure_pct, 2),
        "experiment_mode": experiment_mode or "full",
        **buy_hold,
        **{k: v for k, v in risk.items() if k not in ("drawdown_series", "buy_hold_drawdown_series", "rolling")},
    }

    result["drawdown_series"] = risk["drawdown_series"]
    result["buy_hold_drawdown_series"] = risk["buy_hold_drawdown_series"]
    result["rolling"] = risk["rolling"]

    if fig is not None:
        result["graph"] = json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    return result
