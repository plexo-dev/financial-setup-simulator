---
name: finance-algorithm
description: Build and edit B3 backtest trading algorithms for this simulator. Use when writing process_data, check_buying_conditions, check_selling_conditions, adding files under algorithms/, editing editor_default_values/algorithm.py, or tuning indicators, entries, exits, and reluctant_entry gating.
---

# Finance Algorithm Building

## Contract

Every algorithm is a Python module executed via `exec_user_algorithm()` in `algorithm_helpers.py`. It must define exactly three functions:

| Function | Signature | Returns |
|----------|-----------|---------|
| `process_data` | `(df)` | DataFrame with indicators; call `dropna()` before return |
| `check_buying_conditions` | `(df, price, portfolio)` | `bool` — enter long when flat |
| `check_selling_conditions` | `(df, price, portfolio, comission)` | `bool` — exit when holding |

`df` is the **growing** backtest window: one row per bar, last row = current bar. Use `df["col"].iloc[-1]` (and `iloc[-2]` for crossovers). `price` is the current bar's `Close`.

## Input data

`get_stocks()` returns a yfinance history DataFrame for **B3 tickers only** (`PETR4.SA`, `VALE3.SA`, etc.). Columns include at least `Open`, `High`, `Low`, `Close`, `Volume`.

## Portfolio state

```python
{
    "amount": int,           # shares held (0 when flat)
    "price_bought": float,   # entry price; 0 when flat
    "price_sold": float,     # last sell price; inf if never sold
    "date_bought": int,
    "balance": float,
    "symbol": str,
    # Injected each bar by update_time_state():
    "_bar_index": int,
    "_period_progress": float,   # 0..1 through the window
    "_entry_reluctance": float,  # 1.0 early; rises in final 25%
}
```

Selling only runs when `portfolio["amount"] > 0`. Buying only when flat. Commission is a **decimal** (e.g. `0.01` for 1%).

## reluctant_entry

Import and wrap buy signals:

```python
from algorithm_helpers import reluctant_entry

return reluctant_entry(True, portfolio)   # allowed entry, gated late-window
return reluctant_entry(False, portfolio)  # hard block
```

In the last 25% of bars, `reluctant_entry` probabilistically blocks entries. Tune sensitivity with `portfolio["_entry_reluctance"]` or `_period_progress` (see `algorithms/rsi_reversion.py`, `breakout_20d.py`).

## process_data conventions

- Add indicator columns on `df`; non-OHLCV columns auto-plot on the backtest chart.
- Use private helpers (`_atr`, `_rsi`) at module level — not required by the engine.
- End with `return df.dropna()` so warmup rows are excluded.
- Name columns descriptively (`sma8`, `rsi14`, `atr14`) — they appear in the chart legend.

## Entry / exit patterns

**Entries** (when flat): trend filter (price vs SMA50), signal (crossover, breakout, RSI), anti-churn (skip re-entry near `price_sold`), optional volume confirm.

**Exits** (when holding): always guard `if not portfolio["price_bought"]: return False`. Common exits:
- Hard stop: `price < entry - k * atr`
- Trailing stop: `price < high_n - k * atr` (only if profitable: `price > entry * (1 + comission)`)
- Signal flip: e.g. price below SMA21 while in profit

See [patterns.md](patterns.md) for copy-paste indicator snippets from shipped algorithms.

## New algorithm workflow

1. Copy the closest file from `algorithms/` (trend → `sma8_trend.py`, crossover → `sma_crossover.py`, mean-reversion → `rsi_reversion.py`, breakout → `breakout_20d.py`).
2. Implement the three functions; keep `reluctant_entry` on all buy paths.
3. Smoke-test headless:

```python
from pathlib import Path
from simulator import run_backtest

src = Path("algorithms/my_algo.py").read_text()
r = run_backtest("PETR4.SA", "1y", "1d", src)
print(r["return_pct"], r["buys"], r["sells"])
```

4. Optional: register in `bi_suite.py` `ALGORITHMS` and `ALGORITHM_THEORY` for the BI dashboard.
5. Optional: set as default in `editor_default_values/algorithm.py` for the web form.

## Pitfalls

- `check_selling_conditions` takes `comission` (typo preserved) — use it for profit checks, not as a flat fee subtracted in logic.
- `len(df) < 2` before crossover checks — early bars may have only one row.
- Do not mutate `portfolio` inside condition functions; the engine calls `buy()` / `sell()`.
- `exec()` is local-prototype only — no imports beyond stdlib, pandas, and `algorithm_helpers`.

## Related skills

- Run backtest in browser → `flask-prototype`
- Chart / results presentation → `finance-ux`
