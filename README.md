# Financial Setup Simulator

A web application that simulates financial market trade setups, developed as my final project for the CS50x course.

## Video Demo
**[https://www.youtube.com/watch?v=BCfI9axqTiU](https://www.youtube.com/watch?v=BCfI9axqTiU)**

## Table of Contents
- [General Info](#general-info)
- [Technologies](#technologies)
- [Setup](#setup)

## General Info
This web app serves as a financial market trade setup simulator and was created as the final project for the CS50x course. It is a Flask-based application with two primary pages:
1. An input page for collecting user data.
2. An output page for displaying simulation results.

The simulator operates using custom setups and various market scenarios, allowing users to experiment with different trading strategies.

### Input Page
The input page is divided into three sections:
1. **Stock Selection**:
   - **Input field**: Enter the stock ticker.
   - **Dropdowns**: Choose the time period and time interval.
   - **Buttons**: Submit the form or proceed to the next section.
 
2. **Trading Configuration**:
   - **Input fields**:
 	- Initial balance.
 	- Percentage of capital to use per trade.
 	- Initial number of stocks.
 	- Commission applied to trades.
   - **Button**: Proceed to the next section.

3. **Custom Algorithm & Dependencies**:
   - **Code Input Fields**:
 	- Custom algorithm script.
 	- Additional libraries (if needed).
   - Note: Since the user is also the host of the application, potential security risks from code injection are minimized.

### Output Page
The output page is structured as follows:
- **Header**: Displays the company name, selected period, interval, and total gains.
- **Graph**: Visualizes stock prices along with any indicators specified in the custom algorithm.
- **Log**: Provides a detailed record of operations and their results.

## Technologies

### Python Libraries
- **Flask** - 3.0.3
- **Pandas** - 2.2.3
- **Plotly** - 5.24.1
- **yfinance** - 0.2.48
- **Jinja2** - 3.1.4

### CSS Libraries
- **Bootstrap** - 5.1

### Other Technologies
- **Python Version**: 3.12.7
- **Node.js**: 23.1.0
- **HTML Version**: HTML5

## Setup
Ensure you have **npm**, **Python 3**, and **Node.js** installed on your system.

### Clone the Project
```bash
git clone https://github.com/HenriqueOliveiraCoder/financial-setup-simulator
```


### Go to the project directory
```bash
  cd financial-setup-simulator
```

### Install dependencies
```bash
  npm install
```
or alternatively run
```bash
   python3 -m pip install -r requirements.txt
```

### Start the web application
```bash
   npm start
```
or alternatively run
```bash
   python3 -m flask run
```




