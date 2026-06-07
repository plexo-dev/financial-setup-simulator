---
name: visual-regression
description: Run screenshot-driven visual review using the cursor-ide-browser MCP. Use when validating UI polish, responsive layouts, form states, Plotly charts, loading overlay, or before/after visual changes to templates and CSS.
---

# Visual Regression

Use this skill when a change must be judged visually. Charts, forms, and responsive layouts need browser evidence, not just code review.

## Browser Tools

- Use **cursor-ide-browser** MCP: `browser_navigate`, `browser_snapshot`, `browser_take_screenshot`.
- Check console for Plotly/JS errors when the chart is blank.
- Default dev URL: `http://127.0.0.1:5000` (Flask default).

## Capture Matrix

Capture the smallest useful set:

- Desktop: ~1440×900.
- Mobile: ~390×844.
- Key states: index form (default), loading overlay (during POST), backtest results (chart + log), error page.
- After simulation: confirm candlestick chart renders and buy/sell markers appear.

## Review Criteria

- Layout: no overflow, clipping, orphaned elements, or broken alignment.
- Hierarchy: primary content/action is obvious on index and backtest pages.
- State: loading spinner visible during simulation; results page shows name, period, interval, gains.
- Chart: correct size, responsive, no blank render.
- Forms: all sections usable; selects and inputs aligned.

## Output

Report visual findings as:

1. Screenshot context/viewports checked.
2. Regressions or risks, ordered by severity.
3. Concrete fixes.
4. Remaining gaps if a state/viewport was not checked.
