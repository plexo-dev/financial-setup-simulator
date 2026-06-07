from pathlib import Path


def _md_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] + ["---:"] * (len(headers) - 1)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return lines


def render_markdown(payload, algorithm_catalog=None):
    summary = payload["summary"]
    catalog = algorithm_catalog or payload.get("algorithm_catalog") or []
    lines = [
        "# B3 Strategy Benchmark Report",
        "",
        f"**Generated:** {payload['generated_at']}  ",
        f"**Market:** {payload['market']}  ",
        f"**Scenario:** {payload['scenario']}  ",
        f"**Period:** {payload.get('period', '')} / {payload.get('interval', '')}  ",
        "",
        "> Historical simulation — not live trading. Past performance does not guarantee future results.",
        "",
        "## Market context",
        "",
        "Compares strategy runs against buy & hold, Ibovespa, and USD/BRL over the same window.",
        "",
    ]
    lines.extend(_md_table(
        ["Benchmark", "Return"],
        [
            ["Avg strategy", f"{summary['avg_return_pct']:.2f}%"],
            ["Avg buy & hold", f"{summary['avg_buy_hold_pct']:.2f}%"],
            ["Ibovespa (^BVSP)", f"{summary['ibovespa_return_pct']:.2f}%"],
            ["USD/BRL (USDBRL=X)", f"{summary['dollar_return_pct']:.2f}%"],
        ],
    ))
    lines.extend([
        "",
        "## Summary",
        "",
        f"- **Tests:** {payload['test_count']} ({payload['algorithm_count']} algorithms × {payload['stock_count']} stocks)",
        f"- **Best run:** {summary['best_return_pct']:.2f}%",
        f"- **Worst run:** {summary['worst_return_pct']:.2f}%",
        f"- **Profitable runs:** {summary['positive_runs']} / {payload['test_count']}",
        f"- **Beat buy & hold:** {summary['beat_buy_hold_count']} / {payload['test_count']}",
        f"- **Beat Ibovespa:** {summary['beat_ibovespa_count']} / {payload['test_count']}",
        f"- **Beat USD/BRL:** {summary['beat_dollar_count']} / {payload['test_count']}",
        f"- **Avg vs buy & hold:** {summary['avg_vs_buy_hold_pct']:+.2f} pp",
        "",
        "## Algorithms",
        "",
    ])

    for algo in catalog:
        perf = algo.get("performance") or {}
        theory = algo["theory"]
        lines.extend([
            f"### {algo['name']} ({theory['style']})",
            "",
            theory["summary"],
            "",
            f"- **Indicators:** {theory['indicators']}",
            f"- **Buy logic:** {theory['buy']}",
            f"- **Sell logic:** {theory['sell']}",
            "",
        ])
        if perf:
            lines.extend([
                "#### Performance",
                "",
            ])
            lines.extend(_md_table(
                ["Metric", "Value"],
                [
                    ["Avg strategy return", f"{perf['avg_return_pct']:.2f}%"],
                    ["Avg buy & hold", f"{perf['avg_buy_hold_pct']:.2f}%"],
                    ["Avg vs buy & hold", f"{perf['avg_vs_buy_hold_pct']:+.2f} pp"],
                    ["Avg vs Ibovespa", f"{perf['avg_vs_ibovespa_pct']:+.2f} pp"],
                    ["Avg vs USD/BRL", f"{perf['avg_vs_dollar_pct']:+.2f} pp"],
                    ["Best run", f"{perf['best_return_pct']:.2f}% ({perf['best_symbol']})"],
                    ["Worst run", f"{perf['worst_return_pct']:.2f}% ({perf['worst_symbol']})"],
                    ["Beat buy & hold", f"{perf['beat_buy_hold_count']} / {perf['run_count']}"],
                    ["Beat Ibovespa", f"{perf['beat_ibovespa_count']} / {perf['run_count']}"],
                    ["Beat USD/BRL", f"{perf['beat_dollar_count']} / {perf['run_count']}"],
                    ["Profitable runs", f"{perf['positive_runs']} / {perf['run_count']}"],
                ],
            ))
            lines.extend([
                "",
                "#### Per-stock results",
                "",
            ])
            lines.extend(_md_table(
                ["Symbol", "Strategy", "Buy & hold", "vs B&H", "vs Ibov", "vs USD", "Trades", "Position"],
                [
                    [
                        run["symbol"],
                        f"{run['return_pct']:.2f}%",
                        f"{run['buy_hold_return_pct']:.2f}%",
                        f"{run['vs_buy_hold_pct']:+.2f} pp",
                        f"{run['vs_ibovespa_pct']:+.2f} pp",
                        f"{run['vs_dollar_pct']:+.2f} pp",
                        run["trade_count"],
                        run["final_position"],
                    ]
                    for run in perf.get("runs", [])
                ],
            ))
            lines.extend(["", ""])
        lines.extend([
            f"#### Source (`{algo['path']}`)",
            "",
            "```python",
            algo["code"].rstrip(),
            "```",
            "",
        ])

    lines.extend([
        "## All test results",
        "",
    ])
    lines.extend(_md_table(
        ["#", "Algorithm", "Symbol", "Strategy", "Buy & hold", "vs B&H", "vs Ibov", "vs USD", "Position", "Trades"],
        [
            (
                [
                    row["test_id"],
                    row["algorithm"],
                    row["symbol"],
                    "—",
                    "—",
                    "—",
                    "—",
                    "—",
                    "—",
                    f"**Error:** {row.get('error', '')}",
                ]
                if row.get("status") != "ok"
                else [
                    row["test_id"],
                    row["algorithm"],
                    row["symbol"],
                    f"{row['return_pct']:.2f}%",
                    f"{row['buy_hold_return_pct']:.2f}%",
                    f"{row['vs_buy_hold_pct']:+.2f} pp",
                    f"{row['vs_ibovespa_pct']:+.2f} pp",
                    f"{row['vs_dollar_pct']:+.2f} pp",
                    row["final_position"],
                    row["trade_count"],
                ]
            )
            for row in payload["results"]
        ],
    ))

    lines.extend(["", "## Individual test details", ""])
    for row in payload["results"]:
        lines.extend([
            f"### Test #{row['test_id']} · {row['algorithm']} · {row['symbol']}",
            "",
        ])
        if row.get("status") != "ok":
            lines.append(f"**Error:** {row.get('error', 'Unknown error')}")
            lines.extend(["", ""])
            continue

        lines.extend([
            f"- **Company:** {row.get('name') or '—'}",
            f"- **Period:** {row.get('period', payload.get('period', ''))} / {row.get('interval', payload.get('interval', ''))}",
            f"- **Date range:** {row.get('period_start', '—')} → {row.get('period_end', '—')}",
            f"- **Starting balance:** R$ {row['initial_balance']:.2f}",
            f"- **Strategy return:** {row['return_pct']:.2f}%",
            f"- **Buy & hold return:** {row['buy_hold_return_pct']:.2f}%",
            f"- **vs buy & hold:** {row['vs_buy_hold_pct']:+.2f} pp",
            f"- **vs Ibovespa:** {row['vs_ibovespa_pct']:+.2f} pp",
            f"- **vs USD/BRL:** {row['vs_dollar_pct']:+.2f} pp",
            f"- **Trades:** {row['trade_count']} ({row['buys']}B / {row['sells']}S)",
            f"- **Final position:** {row['final_position']} ({row['final_shares']} shares)",
            "",
        ])
        if row.get("output"):
            lines.extend([
                "| Action | Message |",
                "| --- | --- |",
            ])
            for entry in row["output"]:
                message = str(entry.get("Message", "")).replace("|", "\\|")
                lines.append(f"| {entry.get('Action', '')} | {message} |")
        else:
            lines.append("_No trades executed in this run._")
        lines.extend(["", ""])

    lines.append("")
    return "\n".join(lines)


def write_markdown(payload, path=Path("static/bi_report.md"), algorithm_catalog=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(payload, algorithm_catalog=algorithm_catalog), encoding="utf-8")
    return path
