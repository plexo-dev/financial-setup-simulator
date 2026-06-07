# Algorithm patterns (from shipped strategies)

## ATR (14)

```python
def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
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

## SMA stack + slope

```python
df["sma8"] = df["Close"].rolling(window=8).mean()
df["sma21"] = df["Close"].rolling(window=21).mean()
df["sma50"] = df["Close"].rolling(window=50).mean()
df["sma8_slope"] = df["sma8"].diff(5)
```

## Crossover entry (SMA-8 above SMA-21, fresh cross)

```python
if len(df) < 2:
    return reluctant_entry(False, portfolio)
if df["sma8"].iloc[-1] <= df["sma21"].iloc[-1]:
    return reluctant_entry(False, portfolio)
if df["sma8"].iloc[-2] > df["sma21"].iloc[-2]:
    return reluctant_entry(False, portfolio)
```

## Breakout entry (20-day high, shifted)

```python
df["high20"] = df["High"].rolling(window=20).max().shift(1)
# ...
if price <= high20 * 1.002:
    return reluctant_entry(False, portfolio)
```

## Anti-churn after sell

```python
sold = portfolio["price_sold"]
if sold != float("inf") and sold * 0.96 < price < sold * 1.05:
    return reluctant_entry(False, portfolio)
```

## ATR stop + trailing exit

```python
entry = portfolio["price_bought"]
if not entry:
    return False
atr = df["atr14"].iloc[-1]
if price < entry - 3.0 * atr:
    return True
trail = df["high22"].iloc[-1] - 2.5 * atr
if price < trail and price > entry * (1 + comission):
    return True
```

## Volume filter

```python
if "Volume" in df.columns:
    df["vol_avg20"] = df["Volume"].rolling(window=20).mean()
# ...
if df["Volume"].iloc[-1] < df["vol_avg20"].iloc[-1] * 0.85:
    return reluctant_entry(False, portfolio)
```

## Late-window RSI tightening

```python
y = portfolio.get("_entry_reluctance", 1.0)
rsi_limit = 38 - max(0.0, y - 1.0) * 8
if rsi > rsi_limit:
    return reluctant_entry(False, portfolio)
```

## Reference files

| Strategy | File |
|----------|------|
| SMA-8 trend | `algorithms/sma8_trend.py` |
| SMA crossover | `algorithms/sma_crossover.py` |
| RSI reversion | `algorithms/rsi_reversion.py` |
| 20-day breakout | `algorithms/breakout_20d.py` |
| Web default | `editor_default_values/algorithm.py` |
