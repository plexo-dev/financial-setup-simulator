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
                        "date_bought": 0, "balance": initial_balance, "symbol": symbol, "stoploss": 0, "takeprofit": 0}

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
            for column in df:
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
                            {"Action": "Sell", "Message": f"Sold at {'%.2f' % float(price)}; ballance: {'%.2f' % float(portfolio["balance"])}"})

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
                            {"Action": "Buy", "Message": f"Bought at {'%.2f' % float(price)}; ballance: {'%.2f' % float(portfolio["balance"])}"})

            # Prints results in output log
            output.append(
                {"Action": "Summary", "Message": f"Amount: {portfolio["amount"]}, Balance: {'%.2f' % float(portfolio["balance"])} + {'%.2f' % float(portfolio["amount"] * price)}"})
            output.append(
                {"Action": "Summary", "Message": f"Total: {'%.2f' % (float(portfolio["balance"]) + float(portfolio["amount"] * price))}"})
            gains = '%.2f' % (float(portfolio["balance"]) + float(portfolio["amount"] * price))
            output.append(
                {"Action": "Summary", "Message": f"Gains: {'%.2f' % (float(gains) - initial_balance)} | {'%.2f' % ((float(gains)) / initial_balance * 100)}%"})

            # Final fixes to graph
            fig.update_layout(xaxis_rangeslider_visible=False)
            fig.update_xaxes(type="date")
            fig = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

            # Get stock name
            name = get_stock_name(symbol)

            # Render backtest page with graph and output log
            return render_template("backtest.html", output=output, graph=fig, period=period, interval=interval, gains=('%.2f' % (float(gains) - initial_balance)), name=name)
        
        
        # Generic error handling
        except Exception as e:
            return f"Error:\n\n{e}"
