from pathlib import Path

from bi_metrics import BI_METRICS, exit_reason_label, metric_definitions_markdown, position_label


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
        "# Benchmark de estratégias B3 ajustado ao risco",
        "",
        f"**Gerado em:** {payload['generated_at']}  ",
        f"**Mercado:** {payload['market']}  ",
        f"**Cenário:** {payload['scenario']}  ",
        f"**Período:** {payload.get('period', '')} / {payload.get('interval', '')}  ",
        "",
        "> Simulação histórica — não é trading ao vivo. Sharpe usa taxa livre de risco 0%. "
        "Valor de proteção é um composto narrativo, não alpha de Jensen.",
        "",
    ]
    if summary.get("thesis"):
        lines.extend(["## Resumo executivo", "", summary["thesis"], ""])
    if summary.get("conclusion"):
        lines.extend(["", summary["conclusion"], ""])

    lines.extend([
        "",
        "## Eficiência de risco",
        "",
        "_↑ Retorno, Sharpe, captura de alta · ↓ Volatilidade, drawdown máx., captura de baixa (seletiva), runs sem trades_",
        "",
    ])
    lines.extend(_md_table(
        ["Métrica", "Estratégia (média)", "Comprar e manter (média)"],
        [
            ["Retorno", f"{summary.get('avg_return_pct', 0):.2f}%", f"{summary.get('avg_buy_hold_pct', 0):.2f}%"],
            ["Volatilidade (an.)", f"{summary.get('avg_volatility_pct', 0):.1f}%", f"{summary.get('avg_buy_hold_volatility_pct', 0):.1f}%"],
            ["Drawdown máximo", f"{summary.get('avg_max_drawdown_pct', 0):.1f}%", f"{summary.get('avg_buy_hold_max_drawdown_pct', 0):.1f}%"],
            ["Sharpe", f"{summary.get('avg_sharpe', 0):.2f}", f"{summary.get('avg_buy_hold_sharpe', 0):.2f}"],
            ["Captura de baixa", f"{summary.get('avg_downside_capture_pct'):.0f}%" if summary.get('avg_downside_capture_pct') is not None else "—", "100% (ref)"],
            ["Captura de alta", f"{summary.get('avg_upside_capture_pct'):.0f}%" if summary.get('avg_upside_capture_pct') is not None else "—", "100% (ref)"],
            ["Tempo no mercado", f"{summary.get('avg_exposure_pct', 0):.0f}%", "100% (ref)"],
        ],
    ))

    if catalog:
        lines.extend([
            "",
            "## Análise de exposição",
            "",
            "_Baixa exposição = muito em caixa. ↑ Captura de alta · ↓ Captura de baixa (seletiva), runs sem trades_",
            "",
        ])
        lines.extend(_md_table(
            ["Estratégia", "Tempo no mercado", "Média de trades", "Runs sem trades", "Capt. alta", "Capt. baixa"],
            [
                [
                    algo["name"],
                    f"{perf.get('avg_exposure_pct', 0):.1f}%",
                    f"{perf.get('avg_trades', 0):.1f}",
                    f"{perf.get('zero_trade_runs', 0)} / {perf.get('run_count', 0)}",
                    f"{perf.get('avg_upside_capture_pct'):.0f}%" if perf.get("avg_upside_capture_pct") is not None else "—",
                    f"{perf.get('avg_downside_capture_pct'):.0f}%" if perf.get("avg_downside_capture_pct") is not None else "—",
                ]
                for algo in catalog
                for perf in [algo.get("performance") or {}]
                if perf
            ],
        ))

    decomp = summary.get("decomposition") or {}
    if decomp:
        lines.extend([
            "",
            "## Sinal vs motor de risco (A/B/C)",
            "",
            "_↑ Retorno, captura de alta · ↓ DD máx. · Δ retorno vs A: sinalado_",
            "",
        ])
        for algo, rows in decomp.items():
            lines.extend([f"### {algo}", ""])
            lines.extend(_md_table(
                ["Versão", "Retorno", "DD máx.", "Exposição", "Capt. alta", "Δ retorno vs A"],
                [
                    [
                        row["label"],
                        f"{row['avg_return_pct']:.2f}%",
                        f"{row['avg_max_drawdown_pct']:.1f}%",
                        f"{row['avg_exposure_pct']:.1f}%",
                        f"{row.get('avg_upside_capture_pct') or '—'}",
                        f"{row['delta_return_vs_signal_pp']:+.2f} pp",
                    ]
                    for row in rows
                ],
            ))
            lines.append("")

    risk_scores = summary.get("risk_scores") or {}
    if risk_scores:
        lines.extend([
            "",
            "### Score de redução de risco",
            "",
            "_↑ Score maior é melhor_",
            "",
        ])
        lines.extend(_md_table(
            ["Estratégia", "Score"],
            [[name, f"{score:.0f}"] for name, score in sorted(risk_scores.items(), key=lambda x: -x[1])],
        ))

    lines.extend([
        "",
        "## Contexto de mercado",
        "",
        "_↑ Retorno do benchmark · Superar comprar e manter: contagem maior é melhor_",
        "",
    ])
    lines.extend(_md_table(
        ["Benchmark", "Retorno"],
        [
            ["Estratégias (média)", f"{summary['avg_return_pct']:.2f}%"],
            ["Comprar e manter (média)", f"{summary['avg_buy_hold_pct']:.2f}%"],
            ["Ibovespa (^BVSP)", f"{summary['ibovespa_return_pct']:.2f}%"],
            ["USD/BRL (USDBRL=X)", f"{summary['dollar_return_pct']:.2f}%"],
        ],
    ))
    lines.extend([
        "",
        "## Resumo (secundário)",
        "",
        f"- **Testes:** {payload['test_count']} ({payload['algorithm_count']} algoritmos × {payload['stock_count']} papéis)",
        f"- **Superou comprar e manter:** {summary['beat_buy_hold_count']} / {payload['test_count']}",
        f"- **Média vs comprar e manter:** {summary['avg_vs_buy_hold_pct']:+.2f} pp",
        "",
        "## Algoritmos",
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
            f"- **Indicadores:** {theory['indicators']}",
            f"- **Lógica de compra:** {theory['buy']}",
            f"- **Lógica de venda:** {theory['sell']}",
            "",
        ])
        if perf:
            lines.extend(["#### Performance ajustada ao risco", ""])
            lines.extend(_md_table(
                ["Métrica", "Valor"],
                [
                    ["Score de risco", f"{perf.get('risk_score', 0):.0f}"],
                    ["Retorno médio", f"{perf['avg_return_pct']:.2f}%"],
                    ["C&M médio", f"{perf['avg_buy_hold_pct']:.2f}%"],
                    ["Sharpe", f"{perf.get('avg_sharpe', 0):.2f} (C&M {perf.get('avg_buy_hold_sharpe', 0):.2f})"],
                    ["Drawdown máximo", f"{perf.get('avg_max_drawdown_pct', 0):.1f}% (C&M {perf.get('avg_buy_hold_max_drawdown_pct', 0):.1f}%)"],
                    ["Captura de baixa", f"{perf.get('avg_downside_capture_pct') or '—'}"],
                    ["Tempo no mercado", f"{perf.get('avg_exposure_pct', 0):.1f}%"],
                    ["Runs sem trades", f"{perf.get('zero_trade_runs', 0)} / {perf['run_count']}"],
                    ["Superou C&M", f"{perf['beat_buy_hold_count']} / {perf['run_count']}"],
                ],
            ))
            if perf.get("regime_returns"):
                lines.extend(["", "#### Performance por regime", ""])
                rr = perf["regime_returns"]
                lines.extend(_md_table(
                    ["Alta", "Baixa", "Lateral", "Alta vol."],
                    [[f"{rr.get('bull', 0):.1f}%", f"{rr.get('bear', 0):.1f}%", f"{rr.get('sideways', 0):.1f}%", f"{rr.get('high_vol', 0):.1f}%"]],
                ))
            exit_attr = perf.get("exit_attribution") or {}
            if exit_attr.get("by_reason"):
                lines.extend(["", "#### Atribuição de saídas", ""])
                lines.extend(_md_table(
                    ["Razão", "PnL médio %"],
                    [[exit_reason_label(k), f"{v:+.2f}%"] for k, v in exit_attr["by_reason"].items()],
                ))
                if exit_attr.get("by_engine"):
                    eng = exit_attr["by_engine"]
                    lines.append(f"\nMotor de sinal: {eng.get('signal', 0):+.2f}% · Motor de risco: {eng.get('risk', 0):+.2f}%")
            lines.extend(["", "#### Resultados por papel", ""])
            lines.extend(_md_table(
                ["Papel", "Retorno", "Sharpe", "DD máx.", "vs C&M", "Trades"],
                [
                    [
                        run["symbol"],
                        f"{run['return_pct']:.2f}%",
                        f"{run.get('sharpe', 0):.2f}",
                        f"{run.get('max_drawdown_pct', 0):.1f}%",
                        f"{run['vs_buy_hold_pct']:+.2f} pp",
                        run["trade_count"],
                    ]
                    for run in perf.get("runs", [])
                ],
            ))
            lines.extend(["", ""])
        lines.extend([
            f"#### Código-fonte (`{algo['path']}`)",
            "",
            "```python",
            algo["code"].rstrip(),
            "```",
            "",
        ])

    lines.extend(["## Todos os resultados dos testes", ""])
    lines.extend(_md_table(
        ["#", "Algoritmo", "Papel", "Retorno", "Sharpe", "DD máx.", "vs C&M", "Posição"],
        [
            (
                [row["test_id"], row["algorithm"], row["symbol"], "—", "—", "—", "—", f"**Erro:** {row.get('error', '')}"]
                if row.get("status") != "ok"
                else [
                    row["test_id"],
                    row["algorithm"],
                    row["symbol"],
                    f"{row['return_pct']:.2f}%",
                    f"{row.get('sharpe', 0):.2f}",
                    f"{row.get('max_drawdown_pct', 0):.1f}%",
                    f"{row['vs_buy_hold_pct']:+.2f} pp",
                    position_label(row["final_position"]),
                ]
            )
            for row in payload["results"]
        ],
    ))

    lines.extend(["", metric_definitions_markdown()])
    return "\n".join(lines)


def write_markdown(payload, path=Path("static/bi_report.md"), algorithm_catalog=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(payload, algorithm_catalog=algorithm_catalog), encoding="utf-8")
    return path
