---
name: finance-ux
description: Design and review finance/trading user experience: charts, numbers, risk states, trust cues, order/trade flows, market data freshness, semantic colors, and decision support. Use when building trading, portfolio, simulation, chart, quote, or financial dashboard UI.
---

# Finance UX

Financial UI must feel precise, calm, and trustworthy. Avoid casino aesthetics unless the product explicitly asks for it.

## Principles

- Make data freshness visible: timestamp, stale/loading states, retry/error states.
- Use stable number formatting: locale-aware, consistent decimals, compact large values where appropriate.
- Color semantics must be consistent: green/red can mean up/down, profit/loss, or buy/sell — define it and do not mix meanings.
- Risk and irreversible actions need explicit confirmation, clear consequences, and recoverability where possible.
- Separate signal from decoration. Motion can create atmosphere, but it must not obscure prices, axes, labels, or risk states.
- Show uncertainty: simulations and forecasts need assumptions, confidence, or scenario labels.

## Chart Checklist

- Axes/units/timeframe are clear.
- Current value, change, and timeframe are visible.
- Hover/crosshair/tooltip states do not hide key data.
- Empty/loading/error states explain what is missing.
- Colors remain readable for color-blind users; do not rely on red/green alone.
- Mini charts/sparklines should preserve trend, not pretend to be analytical charts.

## Interaction Checklist

- Primary action is clear, but dangerous actions are not over-optimized for accidental clicks.
- Confirmation copy names the asset/action/quantity.
- Disabled states explain requirements when possible.
- Latency states prevent duplicate submissions.
- Auditability matters: show what happened, when, and whether it succeeded.

## Copy Defaults

Prefer concrete labels: `Portfolio value`, `Unrealized P/L`, `Last updated`, `Simulated return`, `Max drawdown`, `Scenario`. Avoid vague headings unless backed by specific content.

## This Project

- Input flow: stock symbol, period, interval, balance, lot size, commission, custom algorithm.
- Output: Plotly candlestick chart with buy/sell markers, trade log table, gains summary.
- Buy markers are red triangles up; sell markers are green triangles down — keep that mapping consistent in any UI changes.
