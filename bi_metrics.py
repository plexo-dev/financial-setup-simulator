"""Rótulos, orientação direcional e tooltips de cálculo das métricas do BI."""

# direction: higher | lower | neutral | context
BI_METRICS = {
    "risk_efficiency": {
        "label": "Eficiência de risco",
        "direction": "neutral",
        "legend": (
            "Sharpe e captura de alta ↑ melhor · Drawdown máx. ↓ melhor · "
            "Captura de baixa ↓ melhor (seletiva) · Runs sem trades ↓ melhor · "
            "Tabela: retorno e Sharpe ↑ · volatilidade e drawdown máx. ↓."
        ),
        "calc": "Métricas de risco do portfólio, média de todos os runs do benchmark vs comprar e manter nos mesmos papéis e janela.",
    },
    "exposure_analysis": {
        "label": "Análise de exposição",
        "direction": "neutral",
        "legend": (
            "Baixa exposição = muito em caixa, não timing seletivo. "
            "Captura de alta ↑ melhor · Captura de baixa ↓ melhor (seletiva) · Runs sem trades ↓ melhor."
        ),
        "calc": "Quanto tempo cada estratégia ficou posicionada vs em caixa. Baixa exposição com baixa captura costuma indicar redução de risco por estar fora do mercado.",
    },
    "decomposition": {
        "label": "Sinal vs motor de risco",
        "direction": "neutral",
        "legend": (
            "Retorno e captura de alta ↑ melhor · DD máx. ↓ melhor · "
            "Exposição: contexto (baixa = menos investido) · Δ retorno vs A: sinalado (± vs só sinal)."
        ),
        "calc": "Três modos experimentais por algoritmo: A só sinal, B adiciona saídas de risco, C é a estratégia completa com filtros de entrada.",
    },
    "market_context": {
        "label": "Contexto de mercado",
        "direction": "neutral",
        "legend": "Retorno do benchmark ↑ melhor · Superar comprar e manter: contagem maior é melhor.",
        "calc": "Retornos do período para Ibovespa, USD/BRL e a matriz de testes — mostra se a janela foi amplamente altista ou mista.",
    },
    "algorithms_catalog": {
        "label": "Algoritmos",
        "direction": "neutral",
        "legend": (
            "Retorno, Sharpe, captura de alta, score de risco e valor de proteção ↑ melhor · "
            "DD máx. e captura de baixa ↓ melhor · vs C&M: excedente com sinal. "
            "Tabela por papel: retorno e Sharpe ↑ · DD máx. ↓ · vs C&M sinalado."
        ),
        "calc": "Performance, teoria e código-fonte de cada estratégia no catálogo do benchmark.",
    },
    "individual_tests": {
        "label": "Testes individuais",
        "direction": "neutral",
        "legend": "Retorno e valor de proteção ↑ melhor · vs benchmarks: excedente com sinal.",
        "calc": "Saída completa do backtest para cada combinação algoritmo × papel na matriz.",
    },
    "regime_performance": {
        "label": "Performance por regime",
        "direction": "neutral",
        "calc": "Retornos diários anualizados da estratégia agrupados por rótulos heurísticos: alta, baixa, lateral, alta volatilidade.",
    },
    "exit_attribution": {
        "label": "Atribuição de saídas",
        "direction": "neutral",
        "calc": "PnL % por round-trip agrupado pela primeira razão de saída disparada (ATR, chandelier, saídas de sinal, etc.).",
    },
    "sharpe": {
        "label": "Sharpe",
        "direction": "higher",
        "target_display": "≥ 0,5 ou superar C&M",
        "calc": (
            "Retorno anualizado menos taxa livre de risco 0%, dividido pela volatilidade anualizada dos "
            "retornos diários do portfólio (252 pregões). Calculado a partir da curva de patrimônio simulada."
        ),
    },
    "buy_hold_sharpe": {
        "label": "Sharpe comprar e manter",
        "direction": "higher",
        "calc": "Mesma fórmula de Sharpe aplicada à curva de comprar e manter nas mesmas datas da estratégia.",
    },
    "max_drawdown": {
        "label": "Drawdown máximo",
        "direction": "lower",
        "target_display": "≪ comprar e manter",
        "calc": (
            "Maior queda pico-a-vale no patrimônio durante a janela, em percentual positivo. "
            "Calculado barra a barra a partir de caixa mais posição marcada a mercado."
        ),
    },
    "buy_hold_max_drawdown": {
        "label": "Drawdown máx. comprar e manter",
        "direction": "lower",
        "calc": "Drawdown máximo na curva alinhada de comprar e manter (100% investido desde a primeira barra).",
    },
    "downside_capture": {
        "label": "Captura de baixa",
        "direction": "context",
        "direction_note": "Meta 20–40% (participar de parte das perdas, não todas)",
        "target_display": "20–40%",
        "calc": (
            "Nos dias em que o retorno diário de comprar e manter é negativo: retorno médio diário da estratégia "
            "dividido pelo de comprar e manter, × 100. 100% = absorveu todas as perdas; 7% ≈ evitou a maior parte."
        ),
    },
    "upside_capture": {
        "label": "Captura de alta",
        "direction": "context",
        "direction_note": "Meta 50–70% (participar dos ganhos mantendo defesa)",
        "target_display": "50–70%",
        "calc": (
            "Nos dias em que o retorno diário de comprar e manter é positivo: retorno médio diário da estratégia "
            "dividido pelo de comprar e manter, × 100. 100% = capturou todos os ganhos."
        ),
    },
    "time_in_market": {
        "label": "Tempo no mercado",
        "direction": "context",
        "direction_note": "Compare com ~100% comprar e manter; % baixo costuma significar muito em caixa",
        "target_display": "15–40%",
        "calc": "Barras com pelo menos uma ação ÷ total de barras na janela do backtest × 100.",
    },
    "exposure": {
        "label": "Exposição",
        "direction": "context",
        "direction_note": "Igual ao tempo no mercado",
        "target_display": "15–40%",
        "calc": "Barras posicionadas ÷ total de barras × 100. Comprar e manter ≈ 100%.",
    },
    "zero_trade_runs": {
        "label": "Runs sem trades",
        "direction": "lower",
        "calc": "Quantidade de backtests em que a estratégia nunca entrou em posição (0 compras e 0 vendas).",
    },
    "return": {
        "label": "Retorno",
        "direction": "higher",
        "calc": "(Patrimônio final − saldo inicial) ÷ saldo inicial × 100. Inclui caixa e posição aberta no último fechamento.",
    },
    "buy_hold_return": {
        "label": "Retorno comprar e manter",
        "direction": "higher",
        "calc": "Retorno de comprar no primeiro fechamento e manter até o último, com o mesmo saldo inicial.",
    },
    "volatility": {
        "label": "Volatilidade (an.)",
        "direction": "lower",
        "target_display": "≪ comprar e manter",
        "calc": "Desvio padrão dos retornos logarítmicos diários na curva de patrimônio × √252, em percentual.",
    },
    "avg_trades": {
        "label": "Média de trades",
        "direction": "neutral",
        "calc": "Média de execuções de compra mais venda por papel (round trips ≈ vendas).",
    },
    "risk_score": {
        "label": "Score de risco",
        "direction": "higher",
        "target_display": "≥ 70",
        "calc": (
            "Composto 0–100: 40% redução normalizada de drawdown vs C&M, 30% redução de volatilidade, "
            "30% melhora de Sharpe — ranqueado entre os cinco algoritmos deste benchmark."
        ),
    },
    "protection_value": {
        "label": "Valor de proteção",
        "direction": "higher",
        "target_display": "> 0 pp",
        "calc": (
            "Composto narrativo (pp): (DD máx. C&M − DD máx. estratégia) + (vol. C&M − vol. estratégia) "
            "− max(0, retorno C&M − retorno estratégia). Não é alpha de Jensen."
        ),
    },
    "vs_buy_hold": {
        "label": "vs comprar e manter",
        "direction": "context",
        "direction_note": "Excedente com sinal (+ supera C&M)",
        "calc": "Retorno da estratégia menos retorno de comprar e manter no mesmo papel e janela, em pontos percentuais.",
    },
    "beat_buy_hold": {
        "label": "Superou comprar e manter",
        "direction": "higher",
        "calc": "Número de runs em que o retorno da estratégia superou comprar e manter.",
    },
    "beat_ibovespa": {
        "label": "Superou Ibovespa",
        "direction": "higher",
        "calc": "Runs em que o retorno da estratégia superou o retorno do Ibovespa (^BVSP) no período.",
    },
    "beat_dollar": {
        "label": "Superou USD/BRL",
        "direction": "higher",
        "calc": "Runs em que o retorno da estratégia superou a variação do USD/BRL no período (indexado).",
    },
    "ibovespa_return": {
        "label": "Ibovespa",
        "direction": "neutral",
        "calc": "Variação percentual do ^BVSP do primeiro ao último fechamento na janela do benchmark.",
    },
    "dollar_return": {
        "label": "USD/BRL",
        "direction": "neutral",
        "calc": "Variação percentual do USDBRL=X na janela (BRL por USD).",
    },
    "tests_run": {
        "label": "Testes executados",
        "direction": "neutral",
        "calc": "Total de backtests: algoritmos × papéis na matriz do benchmark.",
    },
    "delta_return_vs_a": {
        "label": "Δ retorno vs A",
        "direction": "higher",
        "calc": "Retorno médio desta versão da decomposição menos a Versão A (só sinal) para o mesmo algoritmo.",
    },
    "decomposition_version": {
        "label": "Versão",
        "direction": "neutral",
        "calc": "A = sinais centrais · B = A + ATR/chandelier · C = estratégia completa com filtros e entrada relutante.",
    },
    "strategy_name": {
        "label": "Estratégia",
        "direction": "neutral",
        "calc": "Nome do algoritmo no catálogo do benchmark.",
    },
    "symbol": {
        "label": "Papel",
        "direction": "neutral",
        "calc": "Ticker B3 testado neste run.",
    },
    "algorithm": {
        "label": "Algoritmo",
        "direction": "neutral",
        "calc": "Script de estratégia executado neste backtest.",
    },
    "timespan": {
        "label": "Janela",
        "direction": "neutral",
        "calc": "Período e intervalo de barras do yfinance (ex.: 1y / 1d) da simulação.",
    },
    "date_range": {
        "label": "Intervalo de datas",
        "direction": "neutral",
        "calc": "Primeira e última data negociável da série após o warm-up dos indicadores.",
    },
    "trades": {
        "label": "Trades",
        "direction": "neutral",
        "calc": "Total de compras mais vendas no run.",
    },
    "position": {
        "label": "Posição",
        "direction": "neutral",
        "calc": "Estado final: Comprado (com ações), Vendido (zerado após operar) ou Neutro (nunca entrou).",
    },
    "regime_bull": {
        "label": "Alta",
        "direction": "higher",
        "calc": "Retorno diário médio anualizado em barras classificadas como alta (fechamento > MM-50 com inclinação positiva).",
    },
    "regime_bear": {
        "label": "Baixa",
        "direction": "context",
        "direction_note": "Menos negativo pode ser defensivo",
        "calc": "Retorno anualizado em barras de baixa (fechamento < MM-50 com inclinação negativa).",
    },
    "regime_sideways": {
        "label": "Lateral",
        "direction": "neutral",
        "calc": "Retorno anualizado em barras não classificadas como alta, baixa ou alta volatilidade.",
    },
    "regime_high_vol": {
        "label": "Alta vol.",
        "direction": "neutral",
        "calc": "Retorno anualizado quando o ATR(14) está acima do percentil 70 da janela.",
    },
    "exit_attribution_pnl": {
        "label": "PnL médio %",
        "direction": "higher",
        "calc": "Soma do PnL % por round-trip atribuída a cada razão de saída, média entre runs do algoritmo.",
    },
    "signal_engine": {
        "label": "Motor de sinal",
        "direction": "higher",
        "calc": "PnL % agregado de saídas classificadas como sinal (rompimento de MM, RSI, breakout, etc.).",
    },
    "risk_engine": {
        "label": "Motor de risco",
        "direction": "higher",
        "calc": "PnL % agregado de saídas classificadas como risco (stop ATR, trailing chandelier).",
    },
    "best_worst": {
        "label": "Melhor · Pior",
        "direction": "neutral",
        "calc": "Maior e menor retorno % da estratégia entre os dez papéis deste algoritmo.",
    },
    "profitable_runs": {
        "label": "Runs lucrativos",
        "direction": "higher",
        "calc": "Runs com ganho absoluto positivo em moeda.",
    },
    "vs_ibovespa": {
        "label": "vs Ibovespa",
        "direction": "higher",
        "calc": "Retorno da estratégia menos retorno do Ibovespa no período, em pontos percentuais.",
    },
    "vs_dollar": {
        "label": "vs USD/BRL",
        "direction": "higher",
        "calc": "Retorno da estratégia menos variação do USD/BRL no período, em pontos percentuais.",
    },
    "starting_balance": {
        "label": "Saldo inicial",
        "direction": "neutral",
        "calc": "Caixa simulado inicial (R$) para cada run do benchmark.",
    },
    "stock_performance": {
        "label": "Performance do papel",
        "direction": "neutral",
        "calc": "Retorno de comprar e manter deste papel no intervalo do run.",
    },
    "risk_profile": {
        "label": "Perfil de risco",
        "direction": "neutral",
        "calc": "Sharpe, drawdown máximo e captura de baixa do run vs comprar e manter.",
    },
    "final_position": {
        "label": "Final",
        "direction": "neutral",
        "calc": "Ações finais e saldo em caixa após a última barra.",
    },
    "chart_risk_scatter": {
        "label": "Dispersão risco vs retorno",
        "direction": "neutral",
        "calc": "Cada ponto = retorno médio (Y) vs drawdown máximo médio (X) de um algoritmo. Inferior direito = defensivo; superior esquerdo = fraco.",
    },
    "chart_risk_score": {
        "label": "Score de redução de risco",
        "direction": "higher",
        "calc": "Gráfico de barras do score 0–100 ranqueando os algoritmos.",
    },
    "chart_drawdown": {
        "label": "Curva de drawdown",
        "direction": "neutral",
        "calc": "Drawdown diário % do pico para o algoritmo com melhor score de risco vs comprar e manter em um run representativo.",
    },
    "chart_rolling": {
        "label": "Sharpe móvel",
        "direction": "neutral",
        "calc": "Sharpe móvel de 90 pregões a partir dos retornos diários (amostra de runs por algoritmo).",
    },
    "chart_benchmark": {
        "label": "Gráfico de contexto de mercado",
        "direction": "neutral",
        "calc": "Barras com retorno médio de estratégias, comprar e manter, Ibovespa e USD/BRL no período.",
    },
    "chart_ibovespa": {
        "label": "Ibovespa indexado",
        "direction": "neutral",
        "calc": "Fechamento do ^BVSP reindexado a 100 na primeira barra da janela.",
    },
    "chart_dollar": {
        "label": "USD/BRL indexado",
        "direction": "neutral",
        "calc": "USDBRL=X reindexado a 100 na primeira barra.",
    },
    "chart_comparison": {
        "label": "Comparação de retorno bruto",
        "direction": "neutral",
        "calc": "Barras agrupadas do retorno médio da estratégia vs comprar e manter por algoritmo.",
    },
}

POSITION_PT = {
    "Bought": "Comprado",
    "Sold": "Vendido",
    "Neutral": "Neutro",
}

ACTION_PT = {
    "Buy": "Compra",
    "Sell": "Venda",
    "Summary": "Resumo",
}

EXIT_REASON_PT = {
    "ATR stop": "Stop ATR",
    "Chandelier trail": "Trailing chandelier",
    "SMA break": "Rompimento MM",
    "SMA-50 break": "Rompimento MM-50",
    "Bearish cross": "Cruzamento baixista",
    "RSI take profit": "Take profit RSI",
    "RSI overbought": "RSI sobrecomprado",
    "Bollinger take profit": "Take profit Bollinger",
    "Break below 20d low": "Fechamento abaixo mín. 20d",
    "Fakeout exit": "Saída falso rompimento",
    "Unknown exit": "Saída desconhecida",
}


def position_label(value):
    return POSITION_PT.get(value, value)


def action_label(value):
    return ACTION_PT.get(value, value)


def exit_reason_label(value):
    return EXIT_REASON_PT.get(value, value)


def _target_display(metric_id):
    return BI_METRICS.get(metric_id, {}).get("target_display", "")


def score_metric(metric_id, value, context=None):
    """Retorna dict {color, label, target} ou None se não pontuável."""
    if value is None:
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    ctx = context or {}
    target = _target_display(metric_id)

    if metric_id == "upside_capture":
        if 50 <= value <= 70:
            return {"color": "green", "label": "Na meta", "target": target or "50–70%"}
        if 30 <= value < 50:
            return {"color": "yellow", "label": "Abaixo da faixa", "target": target or "50–70%"}
        if value < 30:
            return {"color": "red", "label": "Subparticipação", "target": target or "50–70%"}
        return {"color": "yellow", "label": "Acima da faixa", "target": target or "50–70%"}

    if metric_id == "downside_capture":
        if 20 <= value <= 40:
            return {"color": "green", "label": "Proteção seletiva", "target": target or "20–40%"}
        if 10 <= value < 20 or 40 < value <= 55:
            return {"color": "yellow", "label": "Fora da faixa ideal", "target": target or "20–40%"}
        if value < 10:
            return {"color": "gray", "label": "Muito em caixa (baixa participação)", "target": target or "20–40%"}
        return {"color": "red", "label": "Muita baixa absorvida", "target": target or "20–40%"}

    if metric_id in ("time_in_market", "exposure"):
        if 15 <= value <= 40:
            return {"color": "green", "label": "Participação ativa", "target": target or "15–40%"}
        if 8 <= value < 15 or 40 < value <= 55:
            return {"color": "yellow", "label": "Borda da faixa", "target": target or "15–40%"}
        if value < 8:
            return {"color": "gray", "label": "Subinvestido", "target": target or "15–40%"}
        return {"color": "yellow", "label": "Alta exposição", "target": target or "15–40%"}

    if metric_id == "sharpe":
        bh = ctx.get("buy_hold_sharpe")
        if bh is not None:
            bh = float(bh)
            if value >= max(0.5, bh):
                return {"color": "green", "label": "Forte vs C&M", "target": target or "≥ 0,5 ou superar C&M"}
            if value >= bh - 0.15 or value >= 0.3:
                return {"color": "yellow", "label": "Próximo ao C&M", "target": target or "≥ 0,5 ou superar C&M"}
            return {"color": "red", "label": "Abaixo do C&M", "target": target or "≥ 0,5 ou superar C&M"}
        if value >= 0.5:
            return {"color": "green", "label": "Sólido", "target": target or "≥ 0,5"}
        if value >= 0.25:
            return {"color": "yellow", "label": "Modesto", "target": target or "≥ 0,5"}
        return {"color": "red", "label": "Fraco", "target": target or "≥ 0,5"}

    if metric_id in ("max_drawdown", "volatility"):
        ref = ctx.get("reference")
        if ref is not None and float(ref) > 0:
            ratio = value / float(ref)
            if ratio <= 0.35:
                return {"color": "green", "label": "Muito abaixo do C&M", "target": target or "≪ comprar e manter"}
            if ratio <= 0.6:
                return {"color": "yellow", "label": "Abaixo do C&M", "target": target or "≪ comprar e manter"}
            return {"color": "red", "label": "Risco próximo ao C&M", "target": target or "≪ comprar e manter"}
        if metric_id == "max_drawdown":
            if value <= 5:
                return {"color": "green", "label": "Drawdown baixo", "target": target}
            if value <= 15:
                return {"color": "yellow", "label": "Drawdown moderado", "target": target}
            return {"color": "red", "label": "Drawdown alto", "target": target}
        return None

    if metric_id == "protection_value":
        if value > 10:
            return {"color": "green", "label": "Proteção forte", "target": target or "> 0 pp"}
        if value >= 0:
            return {"color": "yellow", "label": "Proteção modesta", "target": target or "> 0 pp"}
        return {"color": "red", "label": "Sem proteção líquida", "target": target or "> 0 pp"}

    if metric_id == "risk_score":
        if value >= 70:
            return {"color": "green", "label": "Topo", "target": target or "≥ 70"}
        if value >= 40:
            return {"color": "yellow", "label": "Intermediário", "target": target or "≥ 70"}
        return {"color": "red", "label": "Baixo", "target": target or "≥ 70"}

    if metric_id == "zero_trade_runs":
        total = ctx.get("total")
        if total and total > 0:
            ratio = value / float(total)
            if value == 0:
                return {"color": "green", "label": "Todos os papéis operados", "target": "0 runs"}
            if ratio <= 0.2:
                return {"color": "yellow", "label": "Alguns runs ociosos", "target": "Menos é melhor"}
            return {"color": "red", "label": "Muitos runs ociosos", "target": "Menos é melhor"}
        return None

    return None


def metric_definitions_markdown():
    """Apêndice para exportação bi_report.md."""
    lines = ["## Definições de métricas", ""]
    direction_map = {
        "higher": "↑ melhor",
        "lower": "↓ melhor",
        "neutral": "Somente contexto",
        "context": "Ver nota de meta",
    }
    for _key, m in BI_METRICS.items():
        direction = m.get("direction_note") or direction_map.get(m["direction"], "")
        lines.append(f"### {m['label']}")
        if m.get("legend"):
            lines.append(f"**Guia da seção:** {m['legend']}")
        if direction:
            lines.append(f"**Orientação:** {direction}")
        if m.get("target_display"):
            lines.append(f"**Meta:** {m['target_display']}")
        lines.append(f"{m['calc']}")
        lines.append("")
    return "\n".join(lines)
