from flask import Flask, render_template, request
from utis import get_stocks, buy, sell, get_amount, get_stock_name
from bi_suite import load_bi_results, save_bi_results

import pandas as pd
import plotly.graph_objects as go
import plotly
import subprocess
import json
import shlex
from collections import defaultdict

# Configure application
app = Flask(__name__)


def _build_bi_charts(results):
    labels = [f"{r['algorithm']}<br>{r['symbol']}" for r in results]
    returns = [r["return_pct"] for r in results]
    colors = ["#198754" if value >= 0 else "#dc3545" for value in returns]

    returns_fig = go.Figure(
        data=[
            go.Bar(
                x=labels,
                y=returns,
                marker_color=colors,
                text=[f"{value:.2f}%" for value in returns],
                textposition="outside",
            )
        ]
    )
    returns_fig.update_layout(
        title="Simulated return by test run",
        yaxis_title="Return (%)",
        xaxis_title="Algorithm · Symbol",
        height=420,
        margin=dict(t=60, b=120),
    )

    by_algorithm = defaultdict(list)
    for row in results:
        if row["status"] == "ok":
            by_algorithm[row["algorithm"]].append(row["return_pct"])

    algo_names = list(by_algorithm.keys())
    algo_avgs = [sum(values) / len(values) for values in by_algorithm.values()]
    algo_colors = ["#198754" if value >= 0 else "#dc3545" for value in algo_avgs]

    algorithms_fig = go.Figure(
        data=[
            go.Bar(
                x=algo_names,
                y=algo_avgs,
                marker_color=algo_colors,
                text=[f"{value:.2f}%" for value in algo_avgs],
                textposition="outside",
            )
        ]
    )
    algorithms_fig.update_layout(
        title="Average simulated return by algorithm",
        yaxis_title="Avg return (%)",
        xaxis_title="Algorithm",
        height=380,
        margin=dict(t=60, b=80),
    )

    return json.dumps(
        {
            "returns": json.loads(json.dumps(returns_fig, cls=plotly.utils.PlotlyJSONEncoder)),
            "algorithms": json.loads(json.dumps(algorithms_fig, cls=plotly.utils.PlotlyJSONEncoder)),
        }
    )


@app.route("/bi")
def bi_dashboard():
    if request.args.get("refresh"):
        data = save_bi_results()
    else:
        data = load_bi_results()

    return render_template(
        "bi.html",
        generated_at=data["generated_at"],
        scenario=data["scenario"],
        test_count=data["test_count"],
        algorithm_count=data["algorithm_count"],
        summary=data["summary"],
        results=data["results"],
        chart_data=_build_bi_charts(data["results"]),
    )

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
            user_functions = {}
            exec(algorithm, user_functions)
            
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
            full_df = get_stocks(symbol, period, interval)

            # Process data according to custom user function
            full_df = user_functions["process_data"](full_df)
            
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
            for index, row in full_df.iterrows():
                # Increasing backtest
                df.loc[index] = row

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

            output.append(
                {"Action": "Summary", "Message": f"Simulated return: {'%.2f' % gain_amount} ({'%.2f' % return_pct}%)"})

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
                name=name,
            )

        # Generic error handling
        except Exception as e:
            return render_template("error.html", message=str(e)), 400
