# Algorithm patterns (from shipped strategies)

## Wilder ATR (14) — fast reaction

```python
def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / window, adjust=False).mean()
```

## Simple ATR (14)

```python
return tr.rolling(window).mean()
```

## RSI (14)

```python
delta = df["Close"].diff()
gain = delta.clip(lower=0).rolling(window=14).mean()
loss = (-delta.clip(upper=0)).rolling(window=14).mean()
rs = gain / loss
df["rsi14"] = 100 - (100 / (1 + rs))
```

## Bollinger upper band (20, 2) — RSI take-profit

```python
df["sma20"] = df["Close"].rolling(window=20).mean()
df["std20"] = df["Close"].rolling(window=20).std()
df["bb_upper"] = df["sma20"] + 2 * df["std20"]
# sell: band touch or near-band with RSI confirmation
if price >= bb_upper:
    return True
if rsi > 55 and price >= bb_upper * 0.99:
    return True
```

## BB width squeeze (breakout filter)

```python
df["bb_width"] = (df["std20"] * 4) / df["sma50"]
df["bb_width_p70"] = df["bb_width"].rolling(100).quantile(0.7)
# buy: only when compressed
if df["bb_width"].iloc[-1] > df["bb_width_p70"].iloc[-1]:
    return reluctant_entry(False, portfolio)
```

## SMA stack + slope (2-bar for fast strategies)

```python
df["sma8"] = df["Close"].rolling(window=8).mean()
df["sma21"] = df["Close"].rolling(window=21).mean()
df["sma50"] = df["Close"].rolling(window=50).mean()
df["sma8_slope"] = df["sma8"].diff(2)
df["sma50_slope"] = df["sma50"].diff(5)
```

## SMA-50 anchoring band (medium trend)

```python
if price < sma50 * 0.98 or price > sma50 * 1.04:
    return reluctant_entry(False, portfolio)
```

## Crossover entry (fresh bullish cross)

```python
if len(df) < 2:
    return reluctant_entry(False, portfolio)
if df["sma50_slope"].iloc[-1] < -df["sma50"].iloc[-1] * 0.005:
    return reluctant_entry(False, portfolio)
if df["sma8"].iloc[-1] <= df["sma21"].iloc[-1]:
    return reluctant_entry(False, portfolio)
if df["sma8"].iloc[-2] > df["sma21"].iloc[-2]:
    return reluctant_entry(False, portfolio)
if df["rsi14"].iloc[-1] > 65:
    return reluctant_entry(False, portfolio)
```

## RSI mean-reversion entry

```python
rsi_limit = 38 - max(0.0, portfolio.get("_entry_reluctance", 1.0) - 1.0) * 8
if rsi > rsi_limit:
    return reluctant_entry(False, portfolio)
if price < df["sma50"].iloc[-1] or df["sma50_slope"].iloc[-1] <= 0:
    return reluctant_entry(False, portfolio)
```

## TA-Lib bullish reversal gate (RSI reversion)

```python
import talib

patterns = [talib.CDLHAMMER, talib.CDLENGULFING, talib.CDLMORNINGSTAR, talib.CDLPIERCING, talib.CDLHARAMI]
# composite bullish_reversal column in process_data
# buy: pattern on current bar or prior bar
if not (df["bullish_reversal"].iloc[-1] or df["bullish_reversal"].iloc[-2]):
    return reluctant_entry(False, portfolio)
```

## Anti-churn after sell

```python
sold = portfolio["price_sold"]
if sold != float("inf") and sold * 0.96 < price < sold * 1.05:
    return reluctant_entry(False, portfolio)
```

## Technical exits (no commission gate)

```python
entry = portfolio["price_bought"]
if not entry:
    return False
atr = df["atr14"].iloc[-1]
if price < entry - 3.0 * atr:
    return True
trail = df["high22"].iloc[-1] - 2.5 * atr
if price < trail:
    return True
```

## Adaptive stop (crossover — tighter below SMA-21)

```python
stop_mult = 2.0 if price < df["sma21"].iloc[-1] else 3.0
if price < entry - stop_mult * atr:
    return True
```

## Breakout fakeout exit

```python
if len(df) >= 2 and price < df["high20"].iloc[-1] and df["Close"].iloc[-2] < df["high20"].iloc[-2]:
    return True
```

## Dynamic extension cap (SMA-8)

```python
y = portfolio.get("_entry_reluctance", 1.0)
ext_limit = 1.035 - max(0.0, y - 1.0) * 0.008
if price > sma8 * ext_limit:
    return reluctant_entry(False, portfolio)
```

## Reference files

| Strategy | File |
|----------|------|
| SMA-8 trend | `algorithms/sma8_trend.py` |
| SMA-20 trend | `algorithms/sma20_trend.py` |
| SMA crossover | `algorithms/sma_crossover.py` |
| RSI reversion | `algorithms/rsi_reversion.py` |
| 20-day breakout | `algorithms/breakout_20d.py` |
| Web default | `editor_default_values/algorithm.py` |
