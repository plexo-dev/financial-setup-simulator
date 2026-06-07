from flask import Flask, Response, render_template, request, send_file
from pathlib import Path
from utis import get_stocks, buy, sell, get_amount, get_stock_name
from algorithm_helpers import exec_user_algorithm, update_time_state
from bi_report import render_markdown
from bi_suite import load_algorithm_catalog, load_bi_results, save_bi_results
from benchmarks import buy_and_hold_metrics, dollar_benchmark, ibovespa_benchmark
from simulator import final_position_label

import pandas as pd
import plotly.graph_objects as go
import plotly
import subprocess
import json
import shlex
from collections import defaultdict

# Configure application
app = Flask(__name__)


def _build_bi_charts(results, market_benchmark, dollar_benchmark_data, summary):
    algo_names = list(dict.fromkeys(row["algorithm"] for row in results if row["status"] == "ok"))

    by_algo_strategy = defaultdict(list)
    by_algo_buy_hold = defaultdict(list)
    for row in results:
        if row["status"] != "ok":
            continue
        by_algo_strategy[row["algorithm"]].append(row["return_pct"])
        by_algo_buy_hold[row["algorithm"]].append(row["buy_hold_return_pct"])

    strategy_avgs = [sum(by_algo_strategy[a]) / len(by_algo_strategy[a]) for a in algo_names]
    buy_hold_avgs = [sum(by_algo_buy_hold[a]) / len(by_algo_buy_hold[a]) for a in algo_names]
    ibov_line = [summary["ibovespa_return_pct"]] * len(algo_names)
    dollar_line = [summary["dollar_return_pct"]] * len(algo_names)

    comparison_fig = go.Figure()
    comparison_fig.add_trace(go.Bar(name="Strategy", x=algo_names, y=strategy_avgs, text=[f"{v:.2f}%" for v in strategy_avgs], textposition="outside"))
    comparison_fig.add_trace(go.Bar(name="Buy & hold", x=algo_names, y=buy_hold_avgs, text=[f"{v:.2f}%" for v in buy_hold_avgs], textposition="outside"))
    comparison_fig.add_trace(go.Scatter(name="Ibovespa", x=algo_names, y=ibov_line, mode="lines+markers", line=dict(color="#6f42c1", width=2)))
    comparison_fig.add_trace(go.Scatter(name="USD/BRL", x=algo_names, y=dollar_line, mode="lines+markers", line=dict(color="#20c997", width=2, dash="dash")))
    comparison_fig.update_layout(
        title="Avg return by algorithm vs buy & hold, Ibovespa and USD/BRL",
        yaxis_title="Return (%)",
        barmode="group",
        height=420,
        margin=dict(t=60, b=80),
    )

    ibov_fig = go.Figure()
    if market_benchmark.get("normalized_series"):
        dates = [point["date"] for point in market_benchmark["normalized_series"]]
        values = [point["index"] for point in market_benchmark["normalized_series"]]
        ibov_fig.add_trace(go.Scatter(x=dates, y=values, mode="lines", name="Ibovespa (indexed)", line=dict(color="#6f42c1", width=2)))
    ibov_fig.update_layout(
        title=f"Ibovespa over {market_benchmark.get('period', '')} / {market_benchmark.get('interval', '')} (start = 100)",
        yaxis_title="Indexed level",
        height=360,
        margin=dict(t=60, b=60),
    )

    dollar_fig = go.Figure()
    if dollar_benchmark_data.get("normalized_series"):
        dates = [point["date"] for point in dollar_benchmark_data["normalized_series"]]
        values = [point["index"] for point in dollar_benchmark_data["normalized_series"]]
        dollar_fig.add_trace(go.Scatter(x=dates, y=values, mode="lines", name="USD/BRL (indexed)", line=dict(color="#20c997", width=2)))
    dollar_fig.update_layout(
        title=f"USD/BRL over {dollar_benchmark_data.get('period', '')} / {dollar_benchmark_data.get('interval', '')} (start = 100)",
        yaxis_title="Indexed BRL per USD",
        height=360,
        margin=dict(t=60, b=60),
    )

    benchmark_fig = go.Figure(
        data=[
            go.Bar(
                x=["Strategies (avg)", "Buy & hold (avg)", "Ibovespa", "USD/BRL"],
                y=[
                    summary["avg_return_pct"],
                    summary["avg_buy_hold_pct"],
                    summary["ibovespa_return_pct"],
                    summary["dollar_return_pct"],
                ],
                marker_color=["#0d6efd", "#fd7e14", "#6f42c1", "#20c997"],
                text=[
                    f"{summary['avg_return_pct']:.2f}%",
                    f"{summary['avg_buy_hold_pct']:.2f}%",
                    f"{summary['ibovespa_return_pct']:.2f}%",
                    f"{summary['dollar_return_pct']:.2f}%",
                ],
                textposition="outside",
            )
        ]
    )
    benchmark_fig.update_layout(
        title="Market context — was the sample period biased?",
        yaxis_title="Return (%)",
        height=340,
        margin=dict(t=60, b=60),
    )

    return json.dumps(
        {
            "comparison": json.loads(json.dumps(comparison_fig, cls=plotly.utils.PlotlyJSONEncoder)),
            "ibovespa": json.loads(json.dumps(ibov_fig, cls=plotly.utils.PlotlyJSONEncoder)),
            "dollar": json.loads(json.dumps(dollar_fig, cls=plotly.utils.PlotlyJSONEncoder)),
            "benchmark": json.loads(json.dumps(benchmark_fig, cls=plotly.utils.PlotlyJSONEncoder)),
        }
    )


def _bi_page_context(data):
    return {
        "generated_at": data["generated_at"],
        "market": data.get("market", "B3 (Bovespa)"),
        "scenario": data["scenario"],
        "test_count": data["test_count"],
        "algorithm_count": data["algorithm_count"],
        "stock_count": data.get("stock_count", 10),
        "period": data.get("period", "1y"),
        "interval": data.get("interval", "1d"),
        "market_benchmark": data.get("market_benchmark", {}),
        "dollar_benchmark": data.get("dollar_benchmark", {}),
        "summary": data["summary"],
        "results": data["results"],
        "algorithm_catalog": load_algorithm_catalog(data["results"]),
        "chart_data": _build_bi_charts(
            data["results"],
            data.get("market_benchmark", {}),
            data.get("dollar_benchmark", {}),
            data["summary"],
        ),
        "report_url": "/bi/report",
        "expanded": False,
        "export_mode": False,
    }


@app.route("/bi")
def bi_dashboard():
    data = load_bi_results(force_refresh=bool(request.args.get("refresh")))
    return render_template("bi.html", **_bi_page_context(data))


@app.route("/bi/export/html")
def bi_export_html():
    data = load_bi_results()
    context = _bi_page_context(data)
    context["expanded"] = True
    context["export_mode"] = True
    context["inline_css"] = Path("static/styles.css").read_text(encoding="utf-8")
    context["bi_page_js"] = Path("static/bi_page.js").read_text(encoding="utf-8")
    html = render_template("bi_export.html", **context)
    return Response(
        html,
        mimetype="text/html; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=bi_benchmark.html"},
    )


@app.route("/bi/export/markdown")
def bi_export_markdown():
    data = load_bi_results()
    catalog = load_algorithm_catalog(data["results"])
    markdown = render_markdown(data, algorithm_catalog=catalog)
    return Response(
        markdown,
        mimetype="text/markdown; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=bi_benchmark.md"},
    )


@app.route("/bi/report")
def bi_report():
    report_path = Path("static/bi_report.md")
    if request.args.get("refresh"):
        save_bi_results()
    elif not report_path.exists():
        load_bi_results()
    return send_file(report_path, mimetype="text/markdown; charset=utf-8")


# Main page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        with open("editor_default_values/algorithm.py") as file:
            algorithm_data = file.read()

        return render_template("index.html", algorithm_data=algorithm_data)
    else:
        try:
            # Read data from POST request
            symbol = str(request.form.get("symbol")).upper()
            interval = str(request.form.get("interval"))
            period = str(request.form.get("period"))
            lot_size = int(request.form.get("lot_size")) / 100
            initial_balance = float(request.form.get("initial_balance"))
            comission = int(request.form.get("comission")) / 100
            initial_stocks = int(request.form.get("initial_stocks"))
            algorithm = request.form.get("algorithm")
            requirements = request.form.get("requirements")

            # Setting up user algortithn custom functions
            user_functions = exec_user_algorithm(algorithm)
            
            # Installing requirements for custom functions
            if requirements != "":
                cmd = f"pip install {requirements}"
                subprocess.run(shlex.split(cmd), check=True)

            # Setting up output log
            output = []
                        
            # Initialize portfolio dict, basically a bank account simulation
            portfolio = {"amount": initial_stocks, "price_bought": 0, "price_sold": float("inf"),
                        "date_bought": 0, "balance": initial_balance, "symbol": symbol}

            # Fetching data from yfinance
            raw_df = get_stocks(symbol, period, interval)
            buy_hold = buy_and_hold_metrics(raw_df, initial_balance)
            ibov = ibovespa_benchmark(period, interval, initial_balance)
            dollar = dollar_benchmark(period, interval, initial_balance)
            full_df = user_functions["process_data"](raw_df)
            
            # Dataframe for backtest, empty
            df = full_df.iloc[:0].copy()
            
            # Init graph
            fig = go.Figure(data=[go.Candlestick(x=full_df.index,
                                                open=full_df["Open"].tolist(), high=full_df["High"].tolist(),
                                                low=full_df["Low"].tolist(), close=full_df["Close"].tolist(),
                                                name="Candlesticks")
                                ])
            
            # Adding custom user function graph lines
            graph_ignore = ["Open", "Low", "High", "Close", "Dividends", "Stock Splits", "Volume"]
            colors = ["yellow", "orange", "cyan", "purple", "blue"]
            for column in full_df:
                if column not in graph_ignore:
                    try:
                        fig.add_trace(go.Scatter(
                            x=full_df.index,
                            y=full_df[column].tolist(),
                            mode="lines",
                            name=column,
                            line=dict(color=colors.pop(), width=1)
                        ))
                    except:
                        fig.add_trace(go.Scatter(
                            x=full_df.index,
                            y=full_df[column].tolist(),
                            mode="lines",
                            name=column,
                            line=dict(width=2)
                        ))

            # Main Loop
            total_bars = len(full_df)
            for bar_index, (index, row) in enumerate(full_df.iterrows(), start=1):
                # Increasing backtest
                df.loc[index] = row
                update_time_state(portfolio, bar_index, total_bars)

                # Atualizing data
                price = float(row["Close"])
                amount = get_amount(lot_size, portfolio["balance"], price)

                # Selling stocks
                if portfolio["amount"]:

                    # Selling algorithm
                    if user_functions["check_selling_conditions"](df, price, portfolio, comission):

                        # Sells Stocks
                        portfolio = sell(portfolio, comission, price)

                        # Update Graph
                        fig.add_trace(go.Scatter(
                            x=[df.index[-1]],
                            y=[df["High"].iloc[-1] * 1.1],
                            mode="markers",
                            showlegend=False,
                            marker=dict(color="green", symbol="triangle-down", size=10),
                            text=f"Price sold: {'%.2f' % float(price)}",
                            hoverinfo="text"
                        ))

                        # For debugging (output log)
                        output.append(
                            {"Action": "Sell", "Message": f"Sold at {'%.2f' % float(price)}; balance: {'%.2f' % float(portfolio['balance'])}"})

                # Buying Session
                else:
                    if user_functions["check_buying_conditions"](df, price, portfolio):

                        # Buys Stocks
                        portfolio = buy(portfolio, price, amount)

                        # Update Graph
                        fig.add_trace(go.Scatter(
                            x=[df.index[-1]],
                            y=[df["Low"].iloc[-1] * 0.9],
                            mode="markers",
                            showlegend=False,
                            marker=dict(color="red", symbol="triangle-up", size=10),
                            text=f"Price bought: {'%.2f' % float(price)}",
                            hoverinfo="text"
                        ))
                        # For debugging (output log)
                        output.append(
                            {"Action": "Buy", "Message": f"Bought at {'%.2f' % float(price)}; balance: {'%.2f' % float(portfolio['balance'])}"})

            # Prints results in output log
            output.append(
                {"Action": "Summary", "Message": f"Amount: {portfolio["amount"]}, Balance: {'%.2f' % float(portfolio["balance"])} + {'%.2f' % float(portfolio["amount"] * price)}"})
            output.append(
                {"Action": "Summary", "Message": f"Total: {'%.2f' % (float(portfolio["balance"]) + float(portfolio["amount"] * price))}"})
            total_value = float(portfolio["balance"]) + float(portfolio["amount"] * price)
            gain_amount = total_value - initial_balance
            return_pct = (gain_amount / initial_balance) * 100 if initial_balance else 0
            vs_buy_hold = return_pct - buy_hold["buy_hold_return_pct"]
            vs_ibovespa = return_pct - ibov["buy_hold_return_pct"]
            vs_dollar = return_pct - dollar["buy_hold_return_pct"]

            output.append(
                {"Action": "Summary", "Message": f"Simulated return: {'%.2f' % gain_amount} ({'%.2f' % return_pct}%)"})

            buys = sum(1 for row in output if row["Action"] == "Buy")
            final_position = final_position_label(portfolio, buys)
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
                        f"Strategy vs buy & hold: {vs_buy_hold:+.2f} pp"
                    ),
                }
            )
            output.append(
                {
                    "Action": "Summary",
                    "Message": (
                        f"Ibovespa: {ibov['buy_hold_return_pct']:.2f}% · "
                        f"Strategy vs Ibovespa: {vs_ibovespa:+.2f} pp"
                    ),
                }
            )
            output.append(
                {
                    "Action": "Summary",
                    "Message": (
                        f"USD/BRL: {dollar['buy_hold_return_pct']:.2f}% · "
                        f"Strategy vs dollar: {vs_dollar:+.2f} pp"
                    ),
                }
            )

            # Final fixes to graph
            fig.update_layout(xaxis_rangeslider_visible=False)
            fig.update_xaxes(type="date")
            fig = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

            # Get stock name
            name = get_stock_name(symbol)

            # Render backtest page with graph and output log
            return render_template(
                "backtest.html",
                output=output,
                graph=fig,
                symbol=symbol,
                period=period,
                interval=interval,
                initial_balance=f"{initial_balance:,.2f}",
                total_value=f"{total_value:,.2f}",
                gain_amount=f"{gain_amount:,.2f}",
                return_pct=f"{return_pct:.2f}",
                gain_positive=gain_amount >= 0,
                final_position=final_position,
                final_shares=int(portfolio["amount"]),
                buy_hold_return_pct=f"{buy_hold['buy_hold_return_pct']:.2f}",
                vs_buy_hold_pct=f"{vs_buy_hold:+.2f}",
                ibovespa_return_pct=f"{ibov['buy_hold_return_pct']:.2f}",
                vs_ibovespa_pct=f"{vs_ibovespa:+.2f}",
                dollar_return_pct=f"{dollar['buy_hold_return_pct']:.2f}",
                vs_dollar_pct=f"{vs_dollar:+.2f}",
                name=name,
            )

        # Generic error handling
        except Exception as e:
            return render_template("error.html", message=str(e)), 400
