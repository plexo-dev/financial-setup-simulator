---
name: accessibility-review
description: Review and improve frontend accessibility for this Flask/Bootstrap app: semantic HTML, keyboard support, focus states, contrast, reduced motion, ARIA, forms, tables, and Plotly charts. Use when building or reviewing templates, CSS, or interactive UI.
---

# Accessibility Review

Use this skill before shipping UI. Accessibility is part of product quality, not a cleanup pass.

## Checklist

- Use semantic HTML first: `button`, `a`, `label`, `nav`, `main`, `section`, `h1-h6`.
- Every interactive element is keyboard reachable and has a visible focus state.
- Focus order follows visual order.
- Names are clear: icon-only buttons need `aria-label`; inputs need associated labels.
- Color is not the only signal. Pair red/green states with text, icon, shape, or label.
- Maintain readable contrast on overlays (e.g. loading screen).
- Respect `prefers-reduced-motion`; provide static alternatives for spinners and transitions.
- Charts expose textual summaries, units, and current values; Plotly tooltips should supplement, not replace, table/log data.
- Loading, empty, error, disabled, hover, active, and selected states are distinguishable.

## Implementation Defaults

- Bootstrap form controls: pair every `input`/`select` with a visible or `visually-hidden` label.
- Use `aria-live="polite"` only for important async status changes (e.g. simulation running).
- Plotly chart container should have a nearby heading or summary; trade log table is the textual equivalent of chart markers.
- Loading overlay: ensure it is announced (`role="status"` / `aria-busy`) and does not trap focus incorrectly.

## Review Output

Lead with issues ordered by severity:

- **Blocker**: keyboard trap, inaccessible primary action, missing form labels, unreadable contrast.
- **High**: unclear focus, motion hazard, chart with no equivalent information in log/summary.
- **Medium**: weak labels, ambiguous state, missing helper/error copy.
- **Low**: polish and consistency.
