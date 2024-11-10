from flask import Flask, render_template, request
from utis import get_stocks, buy, sell, get_amount, get_stock_name

import pandas as pd
import plotly.graph_objects as go
import plotly
import subprocess
import json
import shlex

# Configure application
app = Flask(__name__)

# Main page


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        with open("editor_default_values/algorithm.py") as file:
            algorithm_data = file.read()

        return render_template("index.html", algorithm_data=algorithm_data)
    else:
        try:
            symbol = str(request.form.get("symbol")).upper()
            interval = str(request.form.get("interval"))
            period = str(request.form.get("period"))
            lot_size = int(request.form.get("lot_size")) / 100
            initial_balance = float(request.form.get("initial_balance"))
            comission = int(request.form.get("comission")) / 100
            initial_stocks = int(request.form.get("initial_stocks"))
            algorithm = request.form.get("algorithm")
            requirements = request.form.get("requirements")

            user_functions = {}

            exec(algorithm, user_functions)

            output = pd.DataFrame(columns=["Action", "Message"])

            if requirements != "":
                cmd = f"pip install {requirements}"
                subprocess.run(shlex.split(cmd), check=True)

            price = 0
            # Initialize portfolio dict
            portfolio = {"amount": initial_stocks, "price_bought": 0, "price_sold": float("inf"),
                        "date_bought": 0, "balance": initial_balance, "symbol": symbol, "stoploss": 0, "takeprofit": 0}

            # Fetching data
            full_df = get_stocks(symbol, period, interval)

            # Get stop data
            full_df = user_functions["process_data"](full_df)

            df = pd.DataFrame().reindex_like(full_df).dropna()

            fig = go.Figure(data=[go.Candlestick(x=full_df.index,
                                                open=full_df["Open"], high=full_df["High"],
                                                low=full_df["Low"], close=full_df["Close"],
                                                name="Candlesticks")
                                ])

            graph_ignore = ["Open", "Low", "High", "Close", "Dividends", "Stock Splits", "Volume"]

            colors = ["yellow", "orange", "cyan", "purple", "blue"]

            for column in df:
                if column not in graph_ignore:
                    try:
                        fig.add_trace(go.Scatter(
                            x=full_df.index,
                            y=full_df[column],
                            mode="lines",
                            name=column,
                            line=dict(color=colors.pop(), width=1)
                        ))
                    except:
                        fig.add_trace(go.Scatter(
                            x=full_df.index,
                            y=full_df[column],
                            mode="lines",
                            name=column,
                            line=dict(width=2)
                        ))

            # Main Loop
            for index, row in full_df.iterrows():
                # Increasing backtest
                df = pd.concat([df, pd.DataFrame([row])])

                # Atualizing data
                price = df["Close"].iloc[-1]
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

                        # For debugging
                        output = output._append(
                            {"Action": "Sell", "Message": f"Sold at {'%.2f' % float(price)}; ballance: {'%.2f' % float(portfolio["balance"])}"}, ignore_index=True)

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
                        # For debugging
                        output = output._append(
                            {"Action": "Buy", "Message": f"Bought at {'%.2f' % float(price)}; ballance: {'%.2f' % float(portfolio["balance"])}"}, ignore_index=True)

            # Prints results
            output = output._append(
                {"Action": "Summary", "Message": f"Amount: {portfolio["amount"]}, Balance: {'%.2f' % float(portfolio["balance"])} + {'%.2f' % float(portfolio["amount"] * price)}"}, ignore_index=True)
            output = output._append(
                {"Action": "Summary", "Message": f"Total: {'%.2f' % (float(portfolio["balance"]) + float(portfolio["amount"] * price))}"}, ignore_index=True)
            gains = '%.2f' % (float(portfolio["balance"]) + float(portfolio["amount"] * price))
            output = output._append(
                {"Action": "Summary", "Message": f"Gains: {'%.2f' % (float(gains) - initial_balance)} | {'%.2f' % ((float(gains)) / initial_balance * 100)}%"}, ignore_index=True)

            fig.update_layout(xaxis_rangeslider_visible=False)
            fig = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

            name = get_stock_name(symbol)

            return render_template("backtest.html", output=(output.to_dict(orient="records")), graph=fig, period=period, interval=interval, gains=('%.2f' % (float(gains) - initial_balance)), name=name)
        except Exception as e:
            return f"Error:\n\n{e}"
