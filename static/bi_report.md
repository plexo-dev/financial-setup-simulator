# B3 Strategy Benchmark Report

**Generated:** 2026-06-07 19:12 UTC  
**Market:** B3 (Bovespa)  
**Scenario:** B3 · 5 algorithms × 10 stocks · 1y / 1d · R$ 10,000 starting balance  
**Period:** 1y / 1d  

> Historical simulation — not live trading. Past performance does not guarantee future results.

## Market context

Compares strategy runs against buy & hold, Ibovespa, and USD/BRL over the same window.

| Benchmark | Return |
| --- | ---: |
| Avg strategy | 1.22% |
| Avg buy & hold | 2.18% |
| Ibovespa (^BVSP) | 24.06% |
| USD/BRL (USDBRL=X) | -8.54% |

## Summary

- **Tests:** 50 (5 algorithms × 10 stocks)
- **Best run:** 21.24%
- **Worst run:** -12.28%
- **Profitable runs:** 20 / 50
- **Beat buy & hold:** 25 / 50
- **Beat Ibovespa:** 0 / 50
- **Beat USD/BRL:** 48 / 50
- **Avg vs buy & hold:** -0.96 pp

## Algorithms

### SMA-8 trend (Short-term trend following)

Rides early uptrends using a fast 8-day simple moving average (SMA). The idea is to enter when price is already above short- and medium-term averages and the fast average is still rising — a classic “trade with the trend” setup.

- **Indicators:** SMA-8, SMA-21, SMA-50, 5-bar SMA-8 slope, ATR(14), 22-day high.
- **Buy logic:** Price above SMA-8 with a positive slope; price above SMA-21 and SMA-50; not more than ~3.5% extended above SMA-8; avoids re-buying immediately after a recent sell. Uses reluctant entry to skip marginal signals after losses.
- **Sell logic:** ATR stop-loss (3× ATR below entry), chandelier trail (22-day high − 2.5× ATR), or close below SMA-21 once the trade is profitable after commission.

#### Performance

| Metric | Value |
| --- | ---: |
| Avg strategy return | 2.42% |
| Avg buy & hold | 2.18% |
| Avg vs buy & hold | +0.24 pp |
| Avg vs Ibovespa | -21.64 pp |
| Avg vs USD/BRL | +10.96 pp |
| Best run | 11.08% (RADL3.SA) |
| Worst run | -8.87% (SUZB3.SA) |
| Beat buy & hold | 6 / 10 |
| Beat Ibovespa | 0 / 10 |
| Beat USD/BRL | 9 / 10 |
| Profitable runs | 7 / 10 |

#### Per-stock results

| Symbol | Strategy | Buy & hold | vs B&H | vs Ibov | vs USD | Trades | Position |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ABEV3.SA | 3.55% | 21.94% | -18.38 pp | -20.51 pp | +12.09 pp | 8 | Sold |
| BBAS3.SA | -6.40% | -11.78% | +5.38 pp | -30.46 pp | +2.14 pp | 8 | Sold |
| BBDC4.SA | 7.38% | 18.92% | -11.54 pp | -16.68 pp | +15.92 pp | 6 | Sold |
| CYRE3.SA | 1.86% | -15.65% | +17.51 pp | -22.20 pp | +10.40 pp | 8 | Sold |
| ITUB4.SA | 8.90% | 19.68% | -10.78 pp | -15.16 pp | +17.44 pp | 8 | Sold |
| LREN3.SA | -8.45% | -14.55% | +6.10 pp | -32.52 pp | +0.09 pp | 6 | Sold |
| RADL3.SA | 11.08% | 21.48% | -10.39 pp | -12.98 pp | +19.62 pp | 10 | Sold |
| RENT3.SA | 6.34% | -3.57% | +9.91 pp | -17.73 pp | +14.87 pp | 10 | Sold |
| SUZB3.SA | -8.87% | -19.36% | +10.49 pp | -32.93 pp | -0.33 pp | 8 | Sold |
| WEGE3.SA | 8.81% | 4.66% | +4.14 pp | -15.26 pp | +17.35 pp | 6 | Sold |


#### Source (`algorithms/sma8_trend.py`)

```python
import pandas as pd
from algorithm_helpers import reluctant_entry


def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / window, adjust=False).mean()


def process_data(df):
    df["sma8"] = df["Close"].rolling(window=8).mean()
    df["sma21"] = df["Close"].rolling(window=21).mean()
    df["sma50"] = df["Close"].rolling(window=50).mean()
    df["sma8_slope"] = df["sma8"].diff(2)
    df["atr14"] = _atr(df)
    df["high22"] = df["High"].rolling(window=22).max()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    if price < entry - 3.0 * atr:
        return True
    trail = df["high22"].iloc[-1] - 2.5 * atr
    if price < trail:
        return True
    if price < df["sma21"].iloc[-1]:
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    sma8 = df["sma8"].iloc[-1]
    if price <= sma8 or df["sma8_slope"].iloc[-1] <= 0:
        return reluctant_entry(False, portfolio)
    if price < df["sma21"].iloc[-1] or price < df["sma50"].iloc[-1]:
        return reluctant_entry(False, portfolio)
    if price > sma8 * 1.035:
        return reluctant_entry(False, portfolio)
    sold = portfolio["price_sold"]
    if sold != float("inf") and sold * 0.96 < price < sold * 1.05:
        return reluctant_entry(False, portfolio)
    return reluctant_entry(True, portfolio)
```

### SMA-20 trend (Medium-term trend following)

A slower cousin of the SMA-8 strategy. The 20-day average filters out more noise and targets sustained moves where medium- and long-term trends align.

- **Indicators:** SMA-20, SMA-50, 5-bar SMA-20 slope, ATR(14), 22-day high.
- **Buy logic:** Price above SMA-20 with rising slope; SMA-20 above SMA-50; price near SMA-50 support; not chasing more than ~4% above SMA-20; cooldown after recent sells.
- **Sell logic:** ATR stop-loss (3× ATR), chandelier trail, or break below SMA-50 when profitable.

#### Performance

| Metric | Value |
| --- | ---: |
| Avg strategy return | 0.40% |
| Avg buy & hold | 2.18% |
| Avg vs buy & hold | -1.78 pp |
| Avg vs Ibovespa | -23.66 pp |
| Avg vs USD/BRL | +8.94 pp |
| Best run | 2.83% (BBDC4.SA) |
| Worst run | -1.19% (SUZB3.SA) |
| Beat buy & hold | 5 / 10 |
| Beat Ibovespa | 0 / 10 |
| Beat USD/BRL | 10 / 10 |
| Profitable runs | 3 / 10 |

#### Per-stock results

| Symbol | Strategy | Buy & hold | vs B&H | vs Ibov | vs USD | Trades | Position |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ABEV3.SA | 0.00% | 21.94% | -21.94 pp | -24.06 pp | +8.54 pp | 0 | Neutral |
| BBAS3.SA | 0.17% | -11.78% | +11.95 pp | -23.89 pp | +8.71 pp | 2 | Sold |
| BBDC4.SA | 2.83% | 18.92% | -16.09 pp | -21.23 pp | +11.37 pp | 2 | Sold |
| CYRE3.SA | 0.00% | -15.65% | +15.65 pp | -24.06 pp | +8.54 pp | 0 | Neutral |
| ITUB4.SA | 2.17% | 19.68% | -17.50 pp | -21.89 pp | +10.71 pp | 2 | Sold |
| LREN3.SA | 0.00% | -14.55% | +14.55 pp | -24.06 pp | +8.54 pp | 0 | Neutral |
| RADL3.SA | 0.00% | 21.48% | -21.48 pp | -24.06 pp | +8.54 pp | 0 | Neutral |
| RENT3.SA | 0.00% | -3.57% | +3.57 pp | -24.06 pp | +8.54 pp | 0 | Neutral |
| SUZB3.SA | -1.19% | -19.36% | +18.18 pp | -25.25 pp | +7.35 pp | 4 | Sold |
| WEGE3.SA | 0.00% | 4.66% | -4.66 pp | -24.06 pp | +8.54 pp | 0 | Neutral |


#### Source (`algorithms/sma20_trend.py`)

```python
import pandas as pd
from algorithm_helpers import reluctant_entry


def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(window).mean()


def process_data(df):
    df["sma20"] = df["Close"].rolling(window=20).mean()
    df["sma50"] = df["Close"].rolling(window=50).mean()
    df["sma20_slope"] = df["sma20"].diff(5)
    df["atr14"] = _atr(df)
    df["high22"] = df["High"].rolling(window=22).max()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    if price < entry - 3.0 * atr:
        return True
    trail = df["high22"].iloc[-1] - 2.5 * atr
    if price < trail:
        return True
    if price < df["sma50"].iloc[-1]:
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    sma20 = df["sma20"].iloc[-1]
    sma50 = df["sma50"].iloc[-1]
    if price <= sma20 or df["sma20_slope"].iloc[-1] <= 0:
        return reluctant_entry(False, portfolio)
    if price < sma50 * 0.995:
        return reluctant_entry(False, portfolio)
    if price > sma50 * 1.03:
        return reluctant_entry(False, portfolio)
    if sma20 < sma50:
        return reluctant_entry(False, portfolio)
    if price > sma20 * 1.04:
        return reluctant_entry(False, portfolio)
    sold = portfolio["price_sold"]
    if sold != float("inf") and sold * 0.96 < price < sold * 1.06:
        return reluctant_entry(False, portfolio)
    return reluctant_entry(True, portfolio)
```

### SMA crossover (Dual moving-average crossover)

A well-known momentum signal: when a fast average crosses above a slow one, momentum may be shifting bullish. This version requires the broader uptrend (price above SMA-50) and volume confirmation.

- **Indicators:** SMA-8, SMA-21, SMA-50, ATR(14), 22-day high, 20-day average volume.
- **Buy logic:** Fresh bullish cross — SMA-8 just crossed above SMA-21 on the current bar; price above SMA-50; volume at least ~85% of its 20-day average.
- **Sell logic:** ATR stop-loss, chandelier trail, or bearish cross (SMA-8 below SMA-21) once profitable.

#### Performance

| Metric | Value |
| --- | ---: |
| Avg strategy return | 2.67% |
| Avg buy & hold | 2.18% |
| Avg vs buy & hold | +0.49 pp |
| Avg vs Ibovespa | -21.39 pp |
| Avg vs USD/BRL | +11.21 pp |
| Best run | 21.24% (RADL3.SA) |
| Worst run | -12.28% (LREN3.SA) |
| Beat buy & hold | 6 / 10 |
| Beat Ibovespa | 0 / 10 |
| Beat USD/BRL | 9 / 10 |
| Profitable runs | 3 / 10 |

#### Per-stock results

| Symbol | Strategy | Buy & hold | vs B&H | vs Ibov | vs USD | Trades | Position |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ABEV3.SA | -2.73% | 21.94% | -24.67 pp | -26.79 pp | +5.81 pp | 4 | Sold |
| BBAS3.SA | -1.72% | -11.78% | +10.06 pp | -25.78 pp | +6.82 pp | 4 | Sold |
| BBDC4.SA | -1.14% | 18.92% | -20.06 pp | -25.20 pp | +7.40 pp | 4 | Sold |
| CYRE3.SA | 7.49% | -15.65% | +23.14 pp | -16.57 pp | +16.03 pp | 4 | Sold |
| ITUB4.SA | 0.00% | 19.68% | -19.68 pp | -24.06 pp | +8.54 pp | 0 | Neutral |
| LREN3.SA | -12.28% | -14.55% | +2.27 pp | -36.35 pp | -3.75 pp | 4 | Sold |
| RADL3.SA | 21.24% | 21.48% | -0.23 pp | -2.82 pp | +29.78 pp | 4 | Sold |
| RENT3.SA | 0.00% | -3.57% | +3.57 pp | -24.06 pp | +8.54 pp | 0 | Neutral |
| SUZB3.SA | 0.00% | -19.36% | +19.36 pp | -24.06 pp | +8.54 pp | 0 | Neutral |
| WEGE3.SA | 15.84% | 4.66% | +11.18 pp | -8.22 pp | +24.38 pp | 4 | Sold |


#### Source (`algorithms/sma_crossover.py`)

```python
import pandas as pd
from algorithm_helpers import reluctant_entry


def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(window).mean()


def process_data(df):
    df["sma8"] = df["Close"].rolling(window=8).mean()
    df["sma21"] = df["Close"].rolling(window=21).mean()
    df["sma50"] = df["Close"].rolling(window=50).mean()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi14"] = 100 - (100 / (1 + rs))
    df["atr14"] = _atr(df)
    df["high22"] = df["High"].rolling(window=22).max()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    if price < entry - 3.0 * atr:
        return True
    trail = df["high22"].iloc[-1] - 2.5 * atr
    if price < trail:
        return True
    if df["sma8"].iloc[-1] < df["sma21"].iloc[-1]:
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    if len(df) < 2:
        return reluctant_entry(False, portfolio)
    if price < df["sma50"].iloc[-1]:
        return reluctant_entry(False, portfolio)
    if df["sma8"].iloc[-1] <= df["sma21"].iloc[-1]:
        return reluctant_entry(False, portfolio)
    if df["sma8"].iloc[-2] > df["sma21"].iloc[-2]:
        return reluctant_entry(False, portfolio)
    if df["rsi14"].iloc[-1] > 65:
        return reluctant_entry(False, portfolio)
    return reluctant_entry(True, portfolio)
```

### RSI reversion (Mean reversion in an uptrend)

Buys short-term pullbacks in stocks that are still in a longer uptrend. RSI measures how stretched price is; low RSI after a dip can signal a bounce — but only when the 50-day trend is still intact.

- **Indicators:** RSI(14), SMA-50 and its slope, ATR(14), 10-day high.
- **Buy logic:** RSI below a dynamic threshold (stricter after losing streaks); price above rising SMA-50; RSI not in panic territory (< 25); avoids immediate re-entry near the last sell price.
- **Sell logic:** ATR stop-loss (2.5× ATR), take profit when RSI > 65, or chandelier trail on 10-day high.

#### Performance

| Metric | Value |
| --- | ---: |
| Avg strategy return | -0.75% |
| Avg buy & hold | 2.18% |
| Avg vs buy & hold | -2.93 pp |
| Avg vs Ibovespa | -24.81 pp |
| Avg vs USD/BRL | +7.79 pp |
| Best run | 6.24% (RADL3.SA) |
| Worst run | -3.73% (RENT3.SA) |
| Beat buy & hold | 4 / 10 |
| Beat Ibovespa | 0 / 10 |
| Beat USD/BRL | 10 / 10 |
| Profitable runs | 3 / 10 |

#### Per-stock results

| Symbol | Strategy | Buy & hold | vs B&H | vs Ibov | vs USD | Trades | Position |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ABEV3.SA | 0.13% | 21.94% | -21.81 pp | -23.94 pp | +8.67 pp | 2 | Sold |
| BBAS3.SA | -2.71% | -11.78% | +9.07 pp | -26.78 pp | +5.83 pp | 4 | Sold |
| BBDC4.SA | 0.45% | 18.92% | -18.47 pp | -23.62 pp | +8.99 pp | 2 | Sold |
| CYRE3.SA | -0.80% | -15.65% | +14.85 pp | -24.86 pp | +7.74 pp | 2 | Sold |
| ITUB4.SA | -1.44% | 19.68% | -21.11 pp | -25.50 pp | +7.10 pp | 4 | Sold |
| LREN3.SA | 0.00% | -14.55% | +14.55 pp | -24.06 pp | +8.54 pp | 0 | Neutral |
| RADL3.SA | 6.24% | 21.48% | -15.23 pp | -17.82 pp | +14.78 pp | 4 | Sold |
| RENT3.SA | -3.73% | -3.57% | -0.15 pp | -27.79 pp | +4.81 pp | 4 | Sold |
| SUZB3.SA | -3.45% | -19.36% | +15.92 pp | -27.51 pp | +5.09 pp | 4 | Sold |
| WEGE3.SA | -2.19% | 4.66% | -6.85 pp | -26.25 pp | +6.35 pp | 4 | Sold |


#### Source (`algorithms/rsi_reversion.py`)

```python
import pandas as pd
from algorithm_helpers import reluctant_entry


def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(window).mean()


def process_data(df):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi14"] = 100 - (100 / (1 + rs))
    df["sma50"] = df["Close"].rolling(window=50).mean()
    df["sma50_slope"] = df["sma50"].diff(5)
    df["sma20"] = df["Close"].rolling(window=20).mean()
    df["std20"] = df["Close"].rolling(window=20).std()
    df["bb_upper"] = df["sma20"] + 2 * df["std20"]
    df["atr14"] = _atr(df)
    df["high10"] = df["High"].rolling(window=10).max()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    if price < entry - 2.5 * atr:
        return True
    if price >= df["bb_upper"].iloc[-1]:
        return True
    trail = df["high10"].iloc[-1] - 2.0 * atr
    if price < trail:
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    rsi = df["rsi14"].iloc[-1]
    y = portfolio.get("_entry_reluctance", 1.0)
    rsi_limit = 38 - max(0.0, y - 1.0) * 8
    if rsi > rsi_limit:
        return reluctant_entry(False, portfolio)
    if price < df["sma50"].iloc[-1]:
        return reluctant_entry(False, portfolio)
    if df["sma50_slope"].iloc[-1] <= 0:
        return reluctant_entry(False, portfolio)
    sold = portfolio["price_sold"]
    if sold != float("inf") and sold * 0.97 < price < sold * 1.04:
        return reluctant_entry(False, portfolio)
    return reluctant_entry(True, portfolio)
```

### 20-day breakout (Donchian channel breakout)

Inspired by turtle-style breakout systems: when price closes above the highest high of the prior 20 sessions, it may be starting a new leg up. A long-term filter and volume gate reduce false breaks.

- **Indicators:** 20-day high/low (prior bar), SMA-50, ATR(14), 22-day high, 20-day average volume.
- **Buy logic:** Close above yesterday’s 20-day high; price above SMA-50; volume above ~110% of average (threshold rises after losses); cooldown near last sell.
- **Sell logic:** ATR stop-loss (2.5× ATR), chandelier trail, or close below the 20-day low when profitable.

#### Performance

| Metric | Value |
| --- | ---: |
| Avg strategy return | 1.35% |
| Avg buy & hold | 2.18% |
| Avg vs buy & hold | -0.83 pp |
| Avg vs Ibovespa | -22.72 pp |
| Avg vs USD/BRL | +9.89 pp |
| Best run | 8.75% (BBAS3.SA) |
| Worst run | -4.25% (RENT3.SA) |
| Beat buy & hold | 4 / 10 |
| Beat Ibovespa | 0 / 10 |
| Beat USD/BRL | 10 / 10 |
| Profitable runs | 4 / 10 |

#### Per-stock results

| Symbol | Strategy | Buy & hold | vs B&H | vs Ibov | vs USD | Trades | Position |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ABEV3.SA | 5.79% | 21.94% | -16.15 pp | -18.28 pp | +14.33 pp | 2 | Sold |
| BBAS3.SA | 8.75% | -11.78% | +20.53 pp | -15.31 pp | +17.29 pp | 2 | Sold |
| BBDC4.SA | -1.48% | 18.92% | -20.40 pp | -25.55 pp | +7.05 pp | 2 | Sold |
| CYRE3.SA | 0.00% | -15.65% | +15.65 pp | -24.06 pp | +8.54 pp | 0 | Neutral |
| ITUB4.SA | 6.86% | 19.68% | -12.82 pp | -17.21 pp | +15.39 pp | 2 | Sold |
| LREN3.SA | 1.66% | -14.55% | +16.21 pp | -22.41 pp | +10.20 pp | 2 | Sold |
| RADL3.SA | -2.37% | 21.48% | -23.84 pp | -26.43 pp | +6.17 pp | 2 | Sold |
| RENT3.SA | -4.25% | -3.57% | -0.68 pp | -28.31 pp | +4.29 pp | 4 | Sold |
| SUZB3.SA | 0.00% | -19.36% | +19.36 pp | -24.06 pp | +8.54 pp | 0 | Neutral |
| WEGE3.SA | -1.47% | 4.66% | -6.14 pp | -25.54 pp | +7.07 pp | 2 | Sold |


#### Source (`algorithms/breakout_20d.py`)

```python
import pandas as pd
from algorithm_helpers import reluctant_entry


def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(window).mean()


def process_data(df):
    df["high20"] = df["High"].rolling(window=20).max().shift(1)
    df["low20"] = df["Low"].rolling(window=20).min().shift(1)
    df["sma50"] = df["Close"].rolling(window=50).mean()
    df["std20"] = df["Close"].rolling(window=20).std()
    df["bb_width"] = (df["std20"] * 4) / df["sma50"]
    df["bb_width_ma"] = df["bb_width"].rolling(100).mean()
    df["atr14"] = _atr(df)
    df["high22"] = df["High"].rolling(window=22).max()
    if "Volume" in df.columns:
        df["vol_avg20"] = df["Volume"].rolling(window=20).mean()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    if price < entry - 2.5 * atr:
        return True
    trail = df["high22"].iloc[-1] - 2.5 * atr
    if price < trail:
        return True
    if price < df["low20"].iloc[-1]:
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    high20 = df["high20"].iloc[-1]
    if price <= high20 * 1.002:
        return reluctant_entry(False, portfolio)
    if price < df["sma50"].iloc[-1]:
        return reluctant_entry(False, portfolio)
    if df["bb_width"].iloc[-1] > df["bb_width_ma"].iloc[-1]:
        return reluctant_entry(False, portfolio)
    y = portfolio.get("_entry_reluctance", 1.0)
    vol_mult = 1.1 + max(0.0, y - 1.0) * 0.1
    if "vol_avg20" in df.columns and df["Volume"].iloc[-1] < df["vol_avg20"].iloc[-1] * vol_mult:
        return reluctant_entry(False, portfolio)
    sold = portfolio["price_sold"]
    if sold != float("inf") and sold * 0.97 < price < sold * 1.04:
        return reluctant_entry(False, portfolio)
    return reluctant_entry(True, portfolio)
```

## All test results

| # | Algorithm | Symbol | Strategy | Buy & hold | vs B&H | vs Ibov | vs USD | Position | Trades |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | SMA-8 trend | ITUB4.SA | 8.90% | 19.68% | -10.78 pp | -15.16 pp | +17.44 pp | Sold | 8 |
| 2 | SMA-8 trend | BBDC4.SA | 7.38% | 18.92% | -11.54 pp | -16.68 pp | +15.92 pp | Sold | 6 |
| 3 | SMA-8 trend | RADL3.SA | 11.08% | 21.48% | -10.39 pp | -12.98 pp | +19.62 pp | Sold | 10 |
| 4 | SMA-8 trend | WEGE3.SA | 8.81% | 4.66% | +4.14 pp | -15.26 pp | +17.35 pp | Sold | 6 |
| 5 | SMA-8 trend | ABEV3.SA | 3.55% | 21.94% | -18.38 pp | -20.51 pp | +12.09 pp | Sold | 8 |
| 6 | SMA-8 trend | BBAS3.SA | -6.40% | -11.78% | +5.38 pp | -30.46 pp | +2.14 pp | Sold | 8 |
| 7 | SMA-8 trend | RENT3.SA | 6.34% | -3.57% | +9.91 pp | -17.73 pp | +14.87 pp | Sold | 10 |
| 8 | SMA-8 trend | LREN3.SA | -8.45% | -14.55% | +6.10 pp | -32.52 pp | +0.09 pp | Sold | 6 |
| 9 | SMA-8 trend | CYRE3.SA | 1.86% | -15.65% | +17.51 pp | -22.20 pp | +10.40 pp | Sold | 8 |
| 10 | SMA-8 trend | SUZB3.SA | -8.87% | -19.36% | +10.49 pp | -32.93 pp | -0.33 pp | Sold | 8 |
| 11 | SMA-20 trend | ITUB4.SA | 2.17% | 19.68% | -17.50 pp | -21.89 pp | +10.71 pp | Sold | 2 |
| 12 | SMA-20 trend | BBDC4.SA | 2.83% | 18.92% | -16.09 pp | -21.23 pp | +11.37 pp | Sold | 2 |
| 13 | SMA-20 trend | RADL3.SA | 0.00% | 21.48% | -21.48 pp | -24.06 pp | +8.54 pp | Neutral | 0 |
| 14 | SMA-20 trend | WEGE3.SA | 0.00% | 4.66% | -4.66 pp | -24.06 pp | +8.54 pp | Neutral | 0 |
| 15 | SMA-20 trend | ABEV3.SA | 0.00% | 21.94% | -21.94 pp | -24.06 pp | +8.54 pp | Neutral | 0 |
| 16 | SMA-20 trend | BBAS3.SA | 0.17% | -11.78% | +11.95 pp | -23.89 pp | +8.71 pp | Sold | 2 |
| 17 | SMA-20 trend | RENT3.SA | 0.00% | -3.57% | +3.57 pp | -24.06 pp | +8.54 pp | Neutral | 0 |
| 18 | SMA-20 trend | LREN3.SA | 0.00% | -14.55% | +14.55 pp | -24.06 pp | +8.54 pp | Neutral | 0 |
| 19 | SMA-20 trend | CYRE3.SA | 0.00% | -15.65% | +15.65 pp | -24.06 pp | +8.54 pp | Neutral | 0 |
| 20 | SMA-20 trend | SUZB3.SA | -1.19% | -19.36% | +18.18 pp | -25.25 pp | +7.35 pp | Sold | 4 |
| 21 | SMA crossover | ITUB4.SA | 0.00% | 19.68% | -19.68 pp | -24.06 pp | +8.54 pp | Neutral | 0 |
| 22 | SMA crossover | BBDC4.SA | -1.14% | 18.92% | -20.06 pp | -25.20 pp | +7.40 pp | Sold | 4 |
| 23 | SMA crossover | RADL3.SA | 21.24% | 21.48% | -0.23 pp | -2.82 pp | +29.78 pp | Sold | 4 |
| 24 | SMA crossover | WEGE3.SA | 15.84% | 4.66% | +11.18 pp | -8.22 pp | +24.38 pp | Sold | 4 |
| 25 | SMA crossover | ABEV3.SA | -2.73% | 21.94% | -24.67 pp | -26.79 pp | +5.81 pp | Sold | 4 |
| 26 | SMA crossover | BBAS3.SA | -1.72% | -11.78% | +10.06 pp | -25.78 pp | +6.82 pp | Sold | 4 |
| 27 | SMA crossover | RENT3.SA | 0.00% | -3.57% | +3.57 pp | -24.06 pp | +8.54 pp | Neutral | 0 |
| 28 | SMA crossover | LREN3.SA | -12.28% | -14.55% | +2.27 pp | -36.35 pp | -3.75 pp | Sold | 4 |
| 29 | SMA crossover | CYRE3.SA | 7.49% | -15.65% | +23.14 pp | -16.57 pp | +16.03 pp | Sold | 4 |
| 30 | SMA crossover | SUZB3.SA | 0.00% | -19.36% | +19.36 pp | -24.06 pp | +8.54 pp | Neutral | 0 |
| 31 | RSI reversion | ITUB4.SA | -1.44% | 19.68% | -21.11 pp | -25.50 pp | +7.10 pp | Sold | 4 |
| 32 | RSI reversion | BBDC4.SA | 0.45% | 18.92% | -18.47 pp | -23.62 pp | +8.99 pp | Sold | 2 |
| 33 | RSI reversion | RADL3.SA | 6.24% | 21.48% | -15.23 pp | -17.82 pp | +14.78 pp | Sold | 4 |
| 34 | RSI reversion | WEGE3.SA | -2.19% | 4.66% | -6.85 pp | -26.25 pp | +6.35 pp | Sold | 4 |
| 35 | RSI reversion | ABEV3.SA | 0.13% | 21.94% | -21.81 pp | -23.94 pp | +8.67 pp | Sold | 2 |
| 36 | RSI reversion | BBAS3.SA | -2.71% | -11.78% | +9.07 pp | -26.78 pp | +5.83 pp | Sold | 4 |
| 37 | RSI reversion | RENT3.SA | -3.73% | -3.57% | -0.15 pp | -27.79 pp | +4.81 pp | Sold | 4 |
| 38 | RSI reversion | LREN3.SA | 0.00% | -14.55% | +14.55 pp | -24.06 pp | +8.54 pp | Neutral | 0 |
| 39 | RSI reversion | CYRE3.SA | -0.80% | -15.65% | +14.85 pp | -24.86 pp | +7.74 pp | Sold | 2 |
| 40 | RSI reversion | SUZB3.SA | -3.45% | -19.36% | +15.92 pp | -27.51 pp | +5.09 pp | Sold | 4 |
| 41 | 20-day breakout | ITUB4.SA | 6.86% | 19.68% | -12.82 pp | -17.21 pp | +15.39 pp | Sold | 2 |
| 42 | 20-day breakout | BBDC4.SA | -1.48% | 18.92% | -20.40 pp | -25.55 pp | +7.05 pp | Sold | 2 |
| 43 | 20-day breakout | RADL3.SA | -2.37% | 21.48% | -23.84 pp | -26.43 pp | +6.17 pp | Sold | 2 |
| 44 | 20-day breakout | WEGE3.SA | -1.47% | 4.66% | -6.14 pp | -25.54 pp | +7.07 pp | Sold | 2 |
| 45 | 20-day breakout | ABEV3.SA | 5.79% | 21.94% | -16.15 pp | -18.28 pp | +14.33 pp | Sold | 2 |
| 46 | 20-day breakout | BBAS3.SA | 8.75% | -11.78% | +20.53 pp | -15.31 pp | +17.29 pp | Sold | 2 |
| 47 | 20-day breakout | RENT3.SA | -4.25% | -3.57% | -0.68 pp | -28.31 pp | +4.29 pp | Sold | 4 |
| 48 | 20-day breakout | LREN3.SA | 1.66% | -14.55% | +16.21 pp | -22.41 pp | +10.20 pp | Sold | 2 |
| 49 | 20-day breakout | CYRE3.SA | 0.00% | -15.65% | +15.65 pp | -24.06 pp | +8.54 pp | Neutral | 0 |
| 50 | 20-day breakout | SUZB3.SA | 0.00% | -19.36% | +19.36 pp | -24.06 pp | +8.54 pp | Neutral | 0 |

## Individual test details

### Test #1 · SMA-8 trend · ITUB4.SA

- **Company:** Itaú Unibanco Holding S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 8.90%
- **Buy & hold return:** 19.68%
- **vs buy & hold:** -10.78 pp
- **vs Ibovespa:** -15.16 pp
- **vs USD/BRL:** +17.44 pp
- **Trades:** 8 (4B / 4S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 33.79; balance: 2532.62 |
| Sell | Sold at 33.92; balance: 9952.95 |
| Buy | Bought at 35.71; balance: 2489.61 |
| Sell | Sold at 36.16; balance: 9971.81 |
| Buy | Bought at 38.36; balance: 2530.48 |
| Sell | Sold at 37.49; balance: 9729.89 |
| Buy | Bought at 39.55; balance: 2452.66 |
| Sell | Sold at 46.32; balance: 10890.08 |
| Summary | Final position: Sold (0 shares, cash R$ 10890.08) |
| Summary | Buy & hold: R$ 1967.68 (19.68%) · Strategy vs buy & hold: -10.78 pp |


### Test #2 · SMA-8 trend · BBDC4.SA

- **Company:** Banco Bradesco S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 7.38%
- **Buy & hold return:** 18.92%
- **vs buy & hold:** -11.54 pp
- **vs Ibovespa:** -16.68 pp
- **vs USD/BRL:** +15.92 pp
- **Trades:** 6 (3B / 3S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 15.02; balance: 2502.82 |
| Sell | Sold at 16.36; balance: 10582.61 |
| Buy | Bought at 17.20; balance: 2654.70 |
| Sell | Sold at 17.99; balance: 10865.40 |
| Buy | Bought at 20.88; balance: 2721.85 |
| Sell | Sold at 20.76; balance: 10738.05 |
| Summary | Final position: Sold (0 shares, cash R$ 10738.05) |
| Summary | Buy & hold: R$ 1892.05 (18.92%) · Strategy vs buy & hold: -11.54 pp |


### Test #3 · SMA-8 trend · RADL3.SA

- **Company:** Raia Drogasil S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 11.08%
- **Buy & hold return:** 21.48%
- **vs buy & hold:** -10.39 pp
- **vs Ibovespa:** -12.98 pp
- **vs USD/BRL:** +19.62 pp
- **Trades:** 10 (5B / 5S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 16.97; balance: 2515.13 |
| Sell | Sold at 16.79; balance: 9845.07 |
| Buy | Bought at 17.67; balance: 2477.67 |
| Sell | Sold at 17.02; balance: 9504.35 |
| Buy | Bought at 18.15; balance: 2388.66 |
| Sell | Sold at 22.19; balance: 10998.65 |
| Buy | Bought at 23.34; balance: 2759.92 |
| Sell | Sold at 22.93; balance: 10772.93 |
| Buy | Bought at 24.08; balance: 2704.50 |
| Sell | Sold at 25.34; balance: 11108.48 |
| Summary | Final position: Sold (0 shares, cash R$ 11108.48) |
| Summary | Buy & hold: R$ 2147.54 (21.48%) · Strategy vs buy & hold: -10.39 pp |


### Test #4 · SMA-8 trend · WEGE3.SA

- **Company:** WEG S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 8.81%
- **Buy & hold return:** 4.66%
- **vs buy & hold:** +4.14 pp
- **vs Ibovespa:** -15.26 pp
- **vs USD/BRL:** +17.35 pp
- **Trades:** 6 (3B / 3S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 35.83; balance: 2511.45 |
| Sell | Sold at 42.35; balance: 11274.32 |
| Buy | Bought at 48.59; balance: 2819.67 |
| Sell | Sold at 47.60; balance: 11018.57 |
| Buy | Bought at 51.61; balance: 2761.40 |
| Sell | Sold at 51.26; balance: 10880.68 |
| Summary | Final position: Sold (0 shares, cash R$ 10880.68) |
| Summary | Buy & hold: R$ 466.42 (4.66%) · Strategy vs buy & hold: +4.14 pp |


### Test #5 · SMA-8 trend · ABEV3.SA

- **Company:** Ambev S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 3.55%
- **Buy & hold return:** 21.94%
- **vs buy & hold:** -18.38 pp
- **vs Ibovespa:** -20.51 pp
- **vs USD/BRL:** +12.09 pp
- **Trades:** 8 (4B / 4S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 12.15; balance: 2502.54 |
| Sell | Sold at 11.56; balance: 9562.95 |
| Buy | Bought at 12.51; balance: 2397.47 |
| Sell | Sold at 13.01; balance: 9778.74 |
| Buy | Bought at 13.72; balance: 2452.26 |
| Sell | Sold at 15.57; balance: 10683.50 |
| Buy | Bought at 16.59; balance: 2687.12 |
| Sell | Sold at 16.07; balance: 10355.40 |
| Summary | Final position: Sold (0 shares, cash R$ 10355.40) |
| Summary | Buy & hold: R$ 2193.77 (21.94%) · Strategy vs buy & hold: -18.38 pp |


### Test #6 · SMA-8 trend · BBAS3.SA

- **Company:** Banco do Brasil S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -6.40%
- **Buy & hold return:** -11.78%
- **vs buy & hold:** +5.38 pp
- **vs Ibovespa:** -30.46 pp
- **vs USD/BRL:** +2.14 pp
- **Trades:** 8 (4B / 4S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 20.16; balance: 2501.55 |
| Sell | Sold at 21.26; balance: 10331.63 |
| Buy | Bought at 22.37; balance: 2593.24 |
| Sell | Sold at 21.38; balance: 9916.21 |
| Buy | Bought at 24.77; balance: 2484.58 |
| Sell | Sold at 23.90; balance: 9582.26 |
| Buy | Bought at 25.36; balance: 2404.97 |
| Sell | Sold at 24.82; balance: 9359.94 |
| Summary | Final position: Sold (0 shares, cash R$ 9359.94) |
| Summary | Buy & hold: R$ -1177.70 (-11.78%) · Strategy vs buy & hold: +5.38 pp |


### Test #7 · SMA-8 trend · RENT3.SA

- **Company:** Localiza Rent a Car S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 6.34%
- **Buy & hold return:** -3.57%
- **vs buy & hold:** +9.91 pp
- **vs Ibovespa:** -17.73 pp
- **vs USD/BRL:** +14.87 pp
- **Trades:** 10 (5B / 5S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 35.06; balance: 2532.22 |
| Sell | Sold at 37.33; balance: 10404.31 |
| Buy | Bought at 39.95; balance: 2614.22 |
| Sell | Sold at 43.95; balance: 11099.51 |
| Buy | Bought at 46.39; balance: 2796.42 |
| Sell | Sold at 44.25; balance: 10637.42 |
| Buy | Bought at 49.48; balance: 2670.96 |
| Sell | Sold at 49.87; balance: 10619.19 |
| Buy | Bought at 47.75; balance: 2692.69 |
| Sell | Sold at 48.32; balance: 10633.60 |
| Summary | Final position: Sold (0 shares, cash R$ 10633.60) |
| Summary | Buy & hold: R$ -357.31 (-3.57%) · Strategy vs buy & hold: +9.91 pp |


### Test #8 · SMA-8 trend · LREN3.SA

- **Company:** Lojas Renner S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -8.45%
- **Buy & hold return:** -14.55%
- **vs buy & hold:** +6.10 pp
- **vs Ibovespa:** -32.52 pp
- **vs USD/BRL:** +0.09 pp
- **Trades:** 6 (3B / 3S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 16.18; balance: 2507.10 |
| Sell | Sold at 15.56; balance: 9640.10 |
| Buy | Bought at 14.70; balance: 2420.97 |
| Sell | Sold at 14.59; balance: 9511.34 |
| Buy | Bought at 15.37; balance: 2380.32 |
| Sell | Sold at 14.75; balance: 9154.74 |
| Summary | Final position: Sold (0 shares, cash R$ 9154.74) |
| Summary | Buy & hold: R$ -1455.30 (-14.55%) · Strategy vs buy & hold: +6.10 pp |


### Test #9 · SMA-8 trend · CYRE3.SA

- **Company:** Cyrela Brazil Realty S.A. Empreendimentos e Participações
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 1.86%
- **Buy & hold return:** -15.65%
- **vs buy & hold:** +17.51 pp
- **vs Ibovespa:** -22.20 pp
- **vs USD/BRL:** +10.40 pp
- **Trades:** 8 (4B / 4S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 23.79; balance: 2506.53 |
| Sell | Sold at 22.93; balance: 9657.65 |
| Buy | Bought at 25.60; balance: 2439.58 |
| Sell | Sold at 27.67; balance: 10164.66 |
| Buy | Bought at 31.29; balance: 2560.15 |
| Sell | Sold at 31.81; balance: 10212.83 |
| Buy | Bought at 30.51; balance: 2554.82 |
| Sell | Sold at 30.71; balance: 10185.95 |
| Summary | Final position: Sold (0 shares, cash R$ 10185.95) |
| Summary | Buy & hold: R$ -1564.93 (-15.65%) · Strategy vs buy & hold: +17.51 pp |


### Test #10 · SMA-8 trend · SUZB3.SA

- **Company:** Suzano S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -8.87%
- **Buy & hold return:** -19.36%
- **vs buy & hold:** +10.49 pp
- **vs Ibovespa:** -32.93 pp
- **vs USD/BRL:** -0.33 pp
- **Trades:** 8 (4B / 4S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 52.76; balance: 2507.89 |
| Sell | Sold at 51.37; balance: 9729.71 |
| Buy | Bought at 47.91; balance: 2447.84 |
| Sell | Sold at 47.67; balance: 9621.55 |
| Buy | Bought at 51.67; balance: 2438.76 |
| Sell | Sold at 49.93; balance: 9310.30 |
| Buy | Bought at 56.85; balance: 2374.08 |
| Sell | Sold at 55.79; balance: 9112.92 |
| Summary | Final position: Sold (0 shares, cash R$ 9112.92) |
| Summary | Buy & hold: R$ -1936.34 (-19.36%) · Strategy vs buy & hold: +10.49 pp |


### Test #11 · SMA-20 trend · ITUB4.SA

- **Company:** Itaú Unibanco Holding S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 2.17%
- **Buy & hold return:** 19.68%
- **vs buy & hold:** -17.50 pp
- **vs Ibovespa:** -21.89 pp
- **vs USD/BRL:** +10.71 pp
- **Trades:** 2 (1B / 1S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 32.98; balance: 2512.68 |
| Sell | Sold at 34.28; balance: 10217.47 |
| Summary | Final position: Sold (0 shares, cash R$ 10217.47) |
| Summary | Buy & hold: R$ 1967.68 (19.68%) · Strategy vs buy & hold: -17.50 pp |


### Test #12 · SMA-20 trend · BBDC4.SA

- **Company:** Banco Bradesco S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 2.83%
- **Buy & hold return:** 18.92%
- **vs buy & hold:** -16.09 pp
- **vs Ibovespa:** -21.23 pp
- **vs USD/BRL:** +11.37 pp
- **Trades:** 2 (1B / 1S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 15.51; balance: 2508.07 |
| Sell | Sold at 16.26; balance: 10283.06 |
| Summary | Final position: Sold (0 shares, cash R$ 10283.06) |
| Summary | Buy & hold: R$ 1892.05 (18.92%) · Strategy vs buy & hold: -16.09 pp |


### Test #13 · SMA-20 trend · RADL3.SA

- **Company:** Raia Drogasil S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.00%
- **Buy & hold return:** 21.48%
- **vs buy & hold:** -21.48 pp
- **vs Ibovespa:** -24.06 pp
- **vs USD/BRL:** +8.54 pp
- **Trades:** 0 (0B / 0S)
- **Final position:** Neutral (0 shares)

| Action | Message |
| --- | --- |
| Summary | Final position: Neutral (0 shares, cash R$ 10000.00) |
| Summary | Buy & hold: R$ 2147.54 (21.48%) · Strategy vs buy & hold: -21.48 pp |


### Test #14 · SMA-20 trend · WEGE3.SA

- **Company:** WEG S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.00%
- **Buy & hold return:** 4.66%
- **vs buy & hold:** -4.66 pp
- **vs Ibovespa:** -24.06 pp
- **vs USD/BRL:** +8.54 pp
- **Trades:** 0 (0B / 0S)
- **Final position:** Neutral (0 shares)

| Action | Message |
| --- | --- |
| Summary | Final position: Neutral (0 shares, cash R$ 10000.00) |
| Summary | Buy & hold: R$ 466.42 (4.66%) · Strategy vs buy & hold: -4.66 pp |


### Test #15 · SMA-20 trend · ABEV3.SA

- **Company:** Ambev S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.00%
- **Buy & hold return:** 21.94%
- **vs buy & hold:** -21.94 pp
- **vs Ibovespa:** -24.06 pp
- **vs USD/BRL:** +8.54 pp
- **Trades:** 0 (0B / 0S)
- **Final position:** Neutral (0 shares)

| Action | Message |
| --- | --- |
| Summary | Final position: Neutral (0 shares, cash R$ 10000.00) |
| Summary | Buy & hold: R$ 2193.77 (21.94%) · Strategy vs buy & hold: -21.94 pp |


### Test #16 · SMA-20 trend · BBAS3.SA

- **Company:** Banco do Brasil S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.17%
- **Buy & hold return:** -11.78%
- **vs buy & hold:** +11.95 pp
- **vs Ibovespa:** -23.89 pp
- **vs USD/BRL:** +8.71 pp
- **Trades:** 2 (1B / 1S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 20.47; balance: 2508.06 |
| Sell | Sold at 20.72; balance: 10017.13 |
| Summary | Final position: Sold (0 shares, cash R$ 10017.13) |
| Summary | Buy & hold: R$ -1177.70 (-11.78%) · Strategy vs buy & hold: +11.95 pp |


### Test #17 · SMA-20 trend · RENT3.SA

- **Company:** Localiza Rent a Car S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.00%
- **Buy & hold return:** -3.57%
- **vs buy & hold:** +3.57 pp
- **vs Ibovespa:** -24.06 pp
- **vs USD/BRL:** +8.54 pp
- **Trades:** 0 (0B / 0S)
- **Final position:** Neutral (0 shares)

| Action | Message |
| --- | --- |
| Summary | Final position: Neutral (0 shares, cash R$ 10000.00) |
| Summary | Buy & hold: R$ -357.31 (-3.57%) · Strategy vs buy & hold: +3.57 pp |


### Test #18 · SMA-20 trend · LREN3.SA

- **Company:** Lojas Renner S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.00%
- **Buy & hold return:** -14.55%
- **vs buy & hold:** +14.55 pp
- **vs Ibovespa:** -24.06 pp
- **vs USD/BRL:** +8.54 pp
- **Trades:** 0 (0B / 0S)
- **Final position:** Neutral (0 shares)

| Action | Message |
| --- | --- |
| Summary | Final position: Neutral (0 shares, cash R$ 10000.00) |
| Summary | Buy & hold: R$ -1455.30 (-14.55%) · Strategy vs buy & hold: +14.55 pp |


### Test #19 · SMA-20 trend · CYRE3.SA

- **Company:** Cyrela Brazil Realty S.A. Empreendimentos e Participações
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.00%
- **Buy & hold return:** -15.65%
- **vs buy & hold:** +15.65 pp
- **vs Ibovespa:** -24.06 pp
- **vs USD/BRL:** +8.54 pp
- **Trades:** 0 (0B / 0S)
- **Final position:** Neutral (0 shares)

| Action | Message |
| --- | --- |
| Summary | Final position: Neutral (0 shares, cash R$ 10000.00) |
| Summary | Buy & hold: R$ -1564.93 (-15.65%) · Strategy vs buy & hold: +15.65 pp |


### Test #20 · SMA-20 trend · SUZB3.SA

- **Company:** Suzano S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -1.19%
- **Buy & hold return:** -19.36%
- **vs buy & hold:** +18.18 pp
- **vs Ibovespa:** -25.25 pp
- **vs USD/BRL:** +7.35 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 52.19; balance: 2536.30 |
| Sell | Sold at 51.19; balance: 9782.65 |
| Buy | Bought at 48.42; balance: 2471.85 |
| Sell | Sold at 49.56; balance: 9881.31 |
| Summary | Final position: Sold (0 shares, cash R$ 9881.31) |
| Summary | Buy & hold: R$ -1936.34 (-19.36%) · Strategy vs buy & hold: +18.18 pp |


### Test #21 · SMA crossover · ITUB4.SA

- **Company:** Itaú Unibanco Holding S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.00%
- **Buy & hold return:** 19.68%
- **vs buy & hold:** -19.68 pp
- **vs Ibovespa:** -24.06 pp
- **vs USD/BRL:** +8.54 pp
- **Trades:** 0 (0B / 0S)
- **Final position:** Neutral (0 shares)

| Action | Message |
| --- | --- |
| Summary | Final position: Neutral (0 shares, cash R$ 10000.00) |
| Summary | Buy & hold: R$ 1967.68 (19.68%) · Strategy vs buy & hold: -19.68 pp |


### Test #22 · SMA crossover · BBDC4.SA

- **Company:** Banco Bradesco S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -1.14%
- **Buy & hold return:** 18.92%
- **vs buy & hold:** -20.06 pp
- **vs Ibovespa:** -25.20 pp
- **vs USD/BRL:** +7.40 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 17.23; balance: 2506.73 |
| Sell | Sold at 18.10; balance: 10299.71 |
| Buy | Bought at 20.74; balance: 2583.56 |
| Sell | Sold at 19.83; balance: 9885.96 |
| Summary | Final position: Sold (0 shares, cash R$ 9885.96) |
| Summary | Buy & hold: R$ 1892.05 (18.92%) · Strategy vs buy & hold: -20.06 pp |


### Test #23 · SMA crossover · RADL3.SA

- **Company:** Raia Drogasil S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 21.24%
- **Buy & hold return:** 21.48%
- **vs buy & hold:** -0.23 pp
- **vs Ibovespa:** -2.82 pp
- **vs USD/BRL:** +29.78 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 17.49; balance: 2512.64 |
| Sell | Sold at 22.53; balance: 12058.48 |
| Buy | Bought at 24.55; balance: 3022.98 |
| Sell | Sold at 24.98; balance: 12124.17 |
| Summary | Final position: Sold (0 shares, cash R$ 12124.17) |
| Summary | Buy & hold: R$ 2147.54 (21.48%) · Strategy vs buy & hold: -0.23 pp |


### Test #24 · SMA crossover · WEGE3.SA

- **Company:** WEG S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 15.84%
- **Buy & hold return:** 4.66%
- **vs buy & hold:** +11.18 pp
- **vs Ibovespa:** -8.22 pp
- **vs USD/BRL:** +24.38 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 35.96; balance: 2521.23 |
| Sell | Sold at 42.35; balance: 11242.18 |
| Buy | Bought at 43.39; balance: 2824.25 |
| Sell | Sold at 45.61; balance: 11584.19 |
| Summary | Final position: Sold (0 shares, cash R$ 11584.19) |
| Summary | Buy & hold: R$ 466.42 (4.66%) · Strategy vs buy & hold: +11.18 pp |


### Test #25 · SMA crossover · ABEV3.SA

- **Company:** Ambev S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -2.73%
- **Buy & hold return:** 21.94%
- **vs buy & hold:** -24.67 pp
- **vs Ibovespa:** -26.79 pp
- **vs USD/BRL:** +5.81 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 11.68; balance: 2511.19 |
| Sell | Sold at 11.50; balance: 9809.84 |
| Buy | Bought at 15.45; balance: 2455.64 |
| Sell | Sold at 15.43; balance: 9726.87 |
| Summary | Final position: Sold (0 shares, cash R$ 9726.87) |
| Summary | Buy & hold: R$ 2193.77 (21.94%) · Strategy vs buy & hold: -24.67 pp |


### Test #26 · SMA crossover · BBAS3.SA

- **Company:** Banco do Brasil S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -1.72%
- **Buy & hold return:** -11.78%
- **vs buy & hold:** +10.06 pp
- **vs Ibovespa:** -25.78 pp
- **vs USD/BRL:** +6.82 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 20.59; balance: 2506.32 |
| Sell | Sold at 20.92; balance: 10044.78 |
| Buy | Bought at 21.73; balance: 2527.18 |
| Sell | Sold at 21.31; balance: 9828.29 |
| Summary | Final position: Sold (0 shares, cash R$ 9828.29) |
| Summary | Buy & hold: R$ -1177.70 (-11.78%) · Strategy vs buy & hold: +10.06 pp |


### Test #27 · SMA crossover · RENT3.SA

- **Company:** Localiza Rent a Car S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.00%
- **Buy & hold return:** -3.57%
- **vs buy & hold:** +3.57 pp
- **vs Ibovespa:** -24.06 pp
- **vs USD/BRL:** +8.54 pp
- **Trades:** 0 (0B / 0S)
- **Final position:** Neutral (0 shares)

| Action | Message |
| --- | --- |
| Summary | Final position: Neutral (0 shares, cash R$ 10000.00) |
| Summary | Buy & hold: R$ -357.31 (-3.57%) · Strategy vs buy & hold: +3.57 pp |


### Test #28 · SMA crossover · LREN3.SA

- **Company:** Lojas Renner S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -12.28%
- **Buy & hold return:** -14.55%
- **vs buy & hold:** +2.27 pp
- **vs Ibovespa:** -36.35 pp
- **vs USD/BRL:** -3.75 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 15.44; balance: 2511.60 |
| Sell | Sold at 14.19; balance: 9324.93 |
| Buy | Bought at 15.72; balance: 2345.25 |
| Sell | Sold at 14.62; balance: 8771.62 |
| Summary | Final position: Sold (0 shares, cash R$ 8771.62) |
| Summary | Buy & hold: R$ -1455.30 (-14.55%) · Strategy vs buy & hold: +2.27 pp |


### Test #29 · SMA crossover · CYRE3.SA

- **Company:** Cyrela Brazil Realty S.A. Empreendimentos e Participações
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 7.49%
- **Buy & hold return:** -15.65%
- **vs buy & hold:** +23.14 pp
- **vs Ibovespa:** -16.57 pp
- **vs USD/BRL:** +16.03 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 23.41; balance: 2508.55 |
| Sell | Sold at 22.93; balance: 9773.19 |
| Buy | Bought at 27.78; balance: 2466.72 |
| Sell | Sold at 31.81; balance: 10749.25 |
| Summary | Final position: Sold (0 shares, cash R$ 10749.25) |
| Summary | Buy & hold: R$ -1564.93 (-15.65%) · Strategy vs buy & hold: +23.14 pp |


### Test #30 · SMA crossover · SUZB3.SA

- **Company:** Suzano S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.00%
- **Buy & hold return:** -19.36%
- **vs buy & hold:** +19.36 pp
- **vs Ibovespa:** -24.06 pp
- **vs USD/BRL:** +8.54 pp
- **Trades:** 0 (0B / 0S)
- **Final position:** Neutral (0 shares)

| Action | Message |
| --- | --- |
| Summary | Final position: Neutral (0 shares, cash R$ 10000.00) |
| Summary | Buy & hold: R$ -1936.34 (-19.36%) · Strategy vs buy & hold: +19.36 pp |


### Test #31 · RSI reversion · ITUB4.SA

- **Company:** Itaú Unibanco Holding S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -1.44%
- **Buy & hold return:** 19.68%
- **vs buy & hold:** -21.11 pp
- **vs Ibovespa:** -25.50 pp
- **vs USD/BRL:** +7.10 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 43.96; balance: 2526.89 |
| Sell | Sold at 44.58; balance: 10030.29 |
| Buy | Bought at 43.10; balance: 2531.29 |
| Sell | Sold at 42.52; balance: 9856.34 |
| Summary | Final position: Sold (0 shares, cash R$ 9856.34) |
| Summary | Buy & hold: R$ 1967.68 (19.68%) · Strategy vs buy & hold: -21.11 pp |


### Test #32 · RSI reversion · BBDC4.SA

- **Company:** Banco Bradesco S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.45%
- **Buy & hold return:** 18.92%
- **vs buy & hold:** -18.47 pp
- **vs Ibovespa:** -23.62 pp
- **vs USD/BRL:** +8.99 pp
- **Trades:** 2 (1B / 1S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 15.99; balance: 2515.71 |
| Sell | Sold at 16.25; balance: 10044.81 |
| Summary | Final position: Sold (0 shares, cash R$ 10044.81) |
| Summary | Buy & hold: R$ 1892.05 (18.92%) · Strategy vs buy & hold: -18.47 pp |


### Test #33 · RSI reversion · RADL3.SA

- **Company:** Raia Drogasil S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 6.24%
- **Buy & hold return:** 21.48%
- **vs buy & hold:** -15.23 pp
- **vs Ibovespa:** -17.82 pp
- **vs USD/BRL:** +14.78 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 16.95; balance: 2506.70 |
| Sell | Sold at 19.00; balance: 10818.92 |
| Buy | Bought at 25.34; balance: 2710.15 |
| Sell | Sold at 24.98; balance: 10624.23 |
| Summary | Final position: Sold (0 shares, cash R$ 10624.23) |
| Summary | Buy & hold: R$ 2147.54 (21.48%) · Strategy vs buy & hold: -15.23 pp |


### Test #34 · RSI reversion · WEGE3.SA

- **Company:** WEG S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -2.19%
- **Buy & hold return:** 4.66%
- **vs buy & hold:** -6.85 pp
- **vs Ibovespa:** -26.25 pp
- **vs USD/BRL:** +6.35 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 45.61; balance: 2519.89 |
| Sell | Sold at 46.00; balance: 9988.38 |
| Buy | Bought at 50.17; balance: 2512.98 |
| Sell | Sold at 49.27; balance: 9781.16 |
| Summary | Final position: Sold (0 shares, cash R$ 9781.16) |
| Summary | Buy & hold: R$ 466.42 (4.66%) · Strategy vs buy & hold: -6.85 pp |


### Test #35 · RSI reversion · ABEV3.SA

- **Company:** Ambev S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.13%
- **Buy & hold return:** 21.94%
- **vs buy & hold:** -21.81 pp
- **vs Ibovespa:** -23.94 pp
- **vs USD/BRL:** +8.67 pp
- **Trades:** 2 (1B / 1S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 15.23; balance: 2506.84 |
| Sell | Sold at 15.41; balance: 10012.74 |
| Summary | Final position: Sold (0 shares, cash R$ 10012.74) |
| Summary | Buy & hold: R$ 2193.77 (21.94%) · Strategy vs buy & hold: -21.81 pp |


### Test #36 · RSI reversion · BBAS3.SA

- **Company:** Banco do Brasil S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -2.71%
- **Buy & hold return:** -11.78%
- **vs buy & hold:** +9.07 pp
- **vs Ibovespa:** -26.78 pp
- **vs USD/BRL:** +5.83 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 20.64; balance: 2509.17 |
| Sell | Sold at 20.70; balance: 9949.67 |
| Buy | Bought at 24.06; balance: 2491.21 |
| Sell | Sold at 23.58; balance: 9728.81 |
| Summary | Final position: Sold (0 shares, cash R$ 9728.81) |
| Summary | Buy & hold: R$ -1177.70 (-11.78%) · Strategy vs buy & hold: +9.07 pp |


### Test #37 · RSI reversion · RENT3.SA

- **Company:** Localiza Rent a Car S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -3.73%
- **Buy & hold return:** -3.57%
- **vs buy & hold:** -0.15 pp
- **vs Ibovespa:** -27.79 pp
- **vs USD/BRL:** +4.81 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 35.95; balance: 2521.51 |
| Sell | Sold at 35.92; balance: 9917.17 |
| Buy | Bought at 44.37; balance: 2507.23 |
| Sell | Sold at 43.07; balance: 9627.36 |
| Summary | Final position: Sold (0 shares, cash R$ 9627.36) |
| Summary | Buy & hold: R$ -357.31 (-3.57%) · Strategy vs buy & hold: -0.15 pp |


### Test #38 · RSI reversion · LREN3.SA

- **Company:** Lojas Renner S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.00%
- **Buy & hold return:** -14.55%
- **vs buy & hold:** +14.55 pp
- **vs Ibovespa:** -24.06 pp
- **vs USD/BRL:** +8.54 pp
- **Trades:** 0 (0B / 0S)
- **Final position:** Neutral (0 shares)

| Action | Message |
| --- | --- |
| Summary | Final position: Neutral (0 shares, cash R$ 10000.00) |
| Summary | Buy & hold: R$ -1455.30 (-14.55%) · Strategy vs buy & hold: +14.55 pp |


### Test #39 · RSI reversion · CYRE3.SA

- **Company:** Cyrela Brazil Realty S.A. Empreendimentos e Participações
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -0.80%
- **Buy & hold return:** -15.65%
- **vs buy & hold:** +14.85 pp
- **vs Ibovespa:** -24.86 pp
- **vs USD/BRL:** +7.74 pp
- **Trades:** 2 (1B / 1S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 26.94; balance: 2510.07 |
| Sell | Sold at 26.92; balance: 9920.03 |
| Summary | Final position: Sold (0 shares, cash R$ 9920.03) |
| Summary | Buy & hold: R$ -1564.93 (-15.65%) · Strategy vs buy & hold: +14.85 pp |


### Test #40 · RSI reversion · SUZB3.SA

- **Company:** Suzano S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -3.45%
- **Buy & hold return:** -19.36%
- **vs buy & hold:** +15.92 pp
- **vs Ibovespa:** -27.51 pp
- **vs USD/BRL:** +5.09 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 51.43; balance: 2542.61 |
| Sell | Sold at 50.86; balance: 9843.94 |
| Buy | Bought at 55.79; balance: 2479.09 |
| Sell | Sold at 54.91; balance: 9655.31 |
| Summary | Final position: Sold (0 shares, cash R$ 9655.31) |
| Summary | Buy & hold: R$ -1936.34 (-19.36%) · Strategy vs buy & hold: +15.92 pp |


### Test #41 · 20-day breakout · ITUB4.SA

- **Company:** Itaú Unibanco Holding S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 6.86%
- **Buy & hold return:** 19.68%
- **vs buy & hold:** -12.82 pp
- **vs Ibovespa:** -17.21 pp
- **vs USD/BRL:** +15.39 pp
- **Trades:** 2 (1B / 1S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 41.24; balance: 2535.09 |
| Sell | Sold at 45.48; balance: 10685.52 |
| Summary | Final position: Sold (0 shares, cash R$ 10685.52) |
| Summary | Buy & hold: R$ 1967.69 (19.68%) · Strategy vs buy & hold: -12.82 pp |


### Test #42 · 20-day breakout · BBDC4.SA

- **Company:** Banco Bradesco S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -1.48%
- **Buy & hold return:** 18.92%
- **vs buy & hold:** -20.40 pp
- **vs Ibovespa:** -25.55 pp
- **vs USD/BRL:** +7.05 pp
- **Trades:** 2 (1B / 1S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 20.13; balance: 2512.42 |
| Sell | Sold at 19.93; balance: 9851.62 |
| Summary | Final position: Sold (0 shares, cash R$ 9851.62) |
| Summary | Buy & hold: R$ 1892.05 (18.92%) · Strategy vs buy & hold: -20.40 pp |


### Test #43 · 20-day breakout · RADL3.SA

- **Company:** Raia Drogasil S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -2.37%
- **Buy & hold return:** 21.48%
- **vs buy & hold:** -23.84 pp
- **vs Ibovespa:** -26.43 pp
- **vs USD/BRL:** +6.17 pp
- **Trades:** 2 (1B / 1S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 25.54; balance: 2517.04 |
| Sell | Sold at 24.98; balance: 9763.37 |
| Summary | Final position: Sold (0 shares, cash R$ 9763.37) |
| Summary | Buy & hold: R$ 2147.54 (21.48%) · Strategy vs buy & hold: -23.84 pp |


### Test #44 · 20-day breakout · WEGE3.SA

- **Company:** WEG S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -1.47%
- **Buy & hold return:** 4.66%
- **vs buy & hold:** -6.14 pp
- **vs Ibovespa:** -25.54 pp
- **vs USD/BRL:** +7.07 pp
- **Trades:** 2 (1B / 1S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 49.76; balance: 2535.80 |
| Sell | Sold at 49.27; balance: 9852.75 |
| Summary | Final position: Sold (0 shares, cash R$ 9852.75) |
| Summary | Buy & hold: R$ 466.42 (4.66%) · Strategy vs buy & hold: -6.14 pp |


### Test #45 · 20-day breakout · ABEV3.SA

- **Company:** Ambev S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 5.79%
- **Buy & hold return:** 21.94%
- **vs buy & hold:** -16.15 pp
- **vs Ibovespa:** -18.28 pp
- **vs USD/BRL:** +14.33 pp
- **Trades:** 2 (1B / 1S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 14.31; balance: 2501.56 |
| Sell | Sold at 15.57; balance: 10578.65 |
| Summary | Final position: Sold (0 shares, cash R$ 10578.65) |
| Summary | Buy & hold: R$ 2193.77 (21.94%) · Strategy vs buy & hold: -16.15 pp |


### Test #46 · 20-day breakout · BBAS3.SA

- **Company:** Banco do Brasil S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 8.75%
- **Buy & hold return:** -11.78%
- **vs buy & hold:** +20.53 pp
- **vs Ibovespa:** -15.31 pp
- **vs USD/BRL:** +17.29 pp
- **Trades:** 2 (1B / 1S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 22.00; balance: 2519.26 |
| Sell | Sold at 24.82; balance: 10875.06 |
| Summary | Final position: Sold (0 shares, cash R$ 10875.06) |
| Summary | Buy & hold: R$ -1177.69 (-11.78%) · Strategy vs buy & hold: +20.53 pp |


### Test #47 · 20-day breakout · RENT3.SA

- **Company:** Localiza Rent a Car S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** -4.25%
- **Buy & hold return:** -3.57%
- **vs buy & hold:** -0.68 pp
- **vs Ibovespa:** -28.31 pp
- **vs USD/BRL:** +4.29 pp
- **Trades:** 4 (2B / 2S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 47.15; balance: 2503.41 |
| Sell | Sold at 46.36; balance: 9800.56 |
| Buy | Bought at 49.36; balance: 2495.28 |
| Sell | Sold at 48.32; balance: 9575.13 |
| Summary | Final position: Sold (0 shares, cash R$ 9575.13) |
| Summary | Buy & hold: R$ -357.31 (-3.57%) · Strategy vs buy & hold: -0.68 pp |


### Test #48 · 20-day breakout · LREN3.SA

- **Company:** Lojas Renner S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 1.66%
- **Buy & hold return:** -14.55%
- **vs buy & hold:** +16.21 pp
- **vs Ibovespa:** -22.41 pp
- **vs USD/BRL:** +10.20 pp
- **Trades:** 2 (1B / 1S)
- **Final position:** Sold (0 shares)

| Action | Message |
| --- | --- |
| Buy | Bought at 14.28; balance: 2500.79 |
| Sell | Sold at 14.75; balance: 10165.82 |
| Summary | Final position: Sold (0 shares, cash R$ 10165.82) |
| Summary | Buy & hold: R$ -1455.30 (-14.55%) · Strategy vs buy & hold: +16.21 pp |


### Test #49 · 20-day breakout · CYRE3.SA

- **Company:** Cyrela Brazil Realty S.A. Empreendimentos e Participações
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.00%
- **Buy & hold return:** -15.65%
- **vs buy & hold:** +15.65 pp
- **vs Ibovespa:** -24.06 pp
- **vs USD/BRL:** +8.54 pp
- **Trades:** 0 (0B / 0S)
- **Final position:** Neutral (0 shares)

| Action | Message |
| --- | --- |
| Summary | Final position: Neutral (0 shares, cash R$ 10000.00) |
| Summary | Buy & hold: R$ -1564.93 (-15.65%) · Strategy vs buy & hold: +15.65 pp |


### Test #50 · 20-day breakout · SUZB3.SA

- **Company:** Suzano S.A.
- **Period:** 1y / 1d
- **Date range:** 2025-06-05 → 2026-06-05
- **Starting balance:** R$ 10000.00
- **Strategy return:** 0.00%
- **Buy & hold return:** -19.36%
- **vs buy & hold:** +19.36 pp
- **vs Ibovespa:** -24.06 pp
- **vs USD/BRL:** +8.54 pp
- **Trades:** 0 (0B / 0S)
- **Final position:** Neutral (0 shares)

| Action | Message |
| --- | --- |
| Summary | Final position: Neutral (0 shares, cash R$ 10000.00) |
| Summary | Buy & hold: R$ -1936.34 (-19.36%) · Strategy vs buy & hold: +19.36 pp |


