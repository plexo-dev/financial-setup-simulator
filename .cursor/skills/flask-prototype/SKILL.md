---
name: flask-prototype
description: Run, smoke-test, and iterate on this Flask financial setup simulator. Use when starting the dev server, validating the simulation flow end-to-end, checking backtest output, or preparing a prototype demo.
---

# Flask Prototype

## Stack

- **Backend**: Flask 3, Python 3.12, `utis.py` (yfinance, buy/sell helpers)
- **Frontend**: Jinja2 templates, Bootstrap 5.1, Plotly charts
- **Entry**: `app.py` — routes `/` (input + POST simulation), renders `backtest.html` on success

## Start the App

TA-Lib (candlestick patterns in `rsi_reversion.py`) needs the C library before `pip install TA-Lib`:

```bash
# Arch Linux — NOT in official repos; pick one:

# Option A: AUR (yay / paru)
yay -S ta-lib
# or: paru -S ta-lib

# Option B: build from upstream (no AUR helper)
curl -LJO https://github.com/ta-lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz
tar -xzf ta-lib-0.6.4-src.tar.gz && cd ta-lib-0.6.4
./configure --prefix=/usr && make && sudo make install
cd ..

# Debian/Ubuntu: see https://ta-lib.org/install/ (ta-lib_0.6.4_amd64.deb)

cd /home/hso/repos/financial-setup-simulator
python3 -m pip install -r requirements.txt
python3 -m flask run
```

If `import talib` already works (some pip wheels bundle the lib), skip the system install.

App serves at `http://127.0.0.1:5000`.

## Smoke Test Flow

1. **GET /** — index loads with default algorithm from `editor_default_values/algorithm.py`.
2. **Submit simulation** with:
   - Symbol: e.g. `AAPL`
   - Period: e.g. `1y`
   - Interval: e.g. `1d`
   - Initial balance, lot size (%), commission, initial stocks (defaults usually fine)
   - Algorithm: default SMA-8 trend follower is pre-filled
3. **Expect** `backtest.html` with:
   - Header: stock name, period, interval, gains
   - Plotly candlestick chart with buy (red ▲) / sell (green ▼) markers
   - Log table: Buy/Sell/Summary rows
4. **Error path**: invalid symbol or algorithm error returns plain `Error:\n\n{exception}` — note for UX improvements.

## Key Files

| File | Role |
|------|------|
| `app.py` | Routes, simulation loop, graph building |
| `utis.py` | `get_stocks`, `buy`, `sell`, `get_amount`, `get_stock_name` |
| `templates/index.html` | Multi-section input form |
| `templates/backtest.html` | Results chart + log |
| `templates/layout.html` | Base layout, Bootstrap, styles |
| `static/styles.css` | Custom styles (spinner, etc.) |
| `editor_default_values/algorithm.py` | Default `process_data`, `check_buying_conditions`, `check_selling_conditions` |

## Custom Algorithm Contract

User-submitted Python must define:

- `process_data(df)` → DataFrame with indicators
- `check_buying_conditions(df, price, portfolio)` → bool
- `check_selling_conditions(df, price, portfolio, comission)` → bool

## Testing Notes

- No automated test suite exists yet. Use browser MCP (`visual-regression` skill) for UI checks.
- Simulation hits **yfinance** live — needs network; results vary by market data.
- `exec(algorithm)` and optional `pip install` for requirements: local-only prototype risk.

## Demo Script (quick)

1. Start server.
2. Open `/`, enter `AAPL`, pick `1y` / `1d`, submit.
3. Show chart + trade log + gains on backtest page.
4. Link back to Home works.

When asked to "run tests and create a bit of the prototype", start the server, run this smoke flow, apply `finance-ux` + `taste` for any UI polish, and report findings.
