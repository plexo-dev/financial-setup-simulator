import asyncio
import json
import copy
import os
from datetime import datetime, timezone
from pathlib import Path

from benchmarks import dollar_benchmark, ibovespa_benchmark
from bi_report import write_markdown
from risk_metrics import aggregate_exit_attribution, risk_scores
from simulator import run_backtest
# Balanced B3 basket: mix of gainers, flat, and decliners (not only winners).
BENCHMARK_SYMBOLS = (
    "ITUB4.SA",   # ~+20%
    "BBDC4.SA",   # ~+19%
    "RADL3.SA",   # ~+21%
    "WEGE3.SA",   # ~+5%
    "ABEV3.SA",   # ~+22%
    "BBAS3.SA",   # ~-12%
    "RENT3.SA",   # ~-4%
    "LREN3.SA",   # ~-15%
    "CYRE3.SA",   # ~-16%
    "SUZB3.SA",   # ~-19%
)

ALGORITHMS = {
    "SMA-8 trend": "algorithms/sma8_trend.py",
    "SMA-20 trend": "algorithms/sma20_trend.py",
    "SMA crossover": "algorithms/sma_crossover.py",
    "RSI reversion": "algorithms/rsi_reversion.py",
    "20-day breakout": "algorithms/breakout_20d.py",
}

ALGORITHM_THEORY = {
    "SMA-8 trend": {
        "style": "Short-term trend following",
        "summary": (
            "Rides early uptrends using a fast 8-day simple moving average (SMA). "
            "The idea is to enter when price is already above short- and medium-term "
            "averages and the fast average is still rising — a classic “trade with the trend” setup."
        ),
        "indicators": "SMA-8, SMA-21, SMA-50, 2-bar SMA-8 slope, Wilder ATR(14), 22-day high.",
        "buy": (
            "Price above SMA-8 with a positive 2-bar slope; price above SMA-21 and SMA-50; "
            "dynamic extension cap above SMA-8 (tightens late-window); cooldown after recent sells. "
            "Uses reluctant entry to skip marginal signals."
        ),
        "sell": (
            "ATR stop-loss (3× ATR below entry), chandelier trail (22-day high − 2.5× ATR), "
            "or close below SMA-21 — technical exits fire regardless of commission."
        ),
    },
    "SMA-20 trend": {
        "style": "Medium-term trend following",
        "summary": (
            "A slower cousin of the SMA-8 strategy. The 20-day average filters out more noise "
            "and targets sustained moves where medium- and long-term trends align."
        ),
        "indicators": "SMA-20, SMA-50, 2-bar SMA-20 slope, ATR(14), 22-day high.",
        "buy": (
            "Price above SMA-20 with rising 2-bar slope; SMA-20 above SMA-50; price anchored "
            "within 2–4% of SMA-50; not chasing more than ~4% above SMA-20; relaxed cooldown after sells."
        ),
        "sell": (
            "ATR stop-loss (3× ATR), chandelier trail, or break below SMA-50 — no commission gate."
        ),
    },
    "SMA crossover": {
        "style": "Dual moving-average crossover",
        "summary": (
            "A well-known momentum signal: when a fast average crosses above a slow one, "
            "momentum may be shifting bullish. Requires a rising SMA-50 trend and RSI not overbought."
        ),
        "indicators": "SMA-8, SMA-21, SMA-50, SMA-50 slope, RSI(14), ATR(14), 22-day high.",
        "buy": (
            "Fresh bullish cross — SMA-8 just crossed above SMA-21; price above SMA-50; "
            "SMA-50 not in meaningful decline (> −0.5% over 5 bars); RSI ≤ 65."
        ),
        "sell": (
            "Adaptive ATR stop (2× below SMA-21, else 3×), chandelier trail, or bearish cross — "
            "no commission gate on technical exits."
        ),
    },
    "RSI reversion": {
        "style": "Mean reversion in an uptrend",
        "summary": (
            "Buys short-term pullbacks in stocks that are still in a longer uptrend. "
            "RSI and SMA-50 set context; TA-Lib candlestick patterns confirm timing unless RSI is deeply oversold."
        ),
        "indicators": (
            "RSI(14), SMA-21, SMA-50 and its slope, TA-Lib CDL bullish reversal composite, "
            "Bollinger upper (20, 2), Wilder ATR(14), 22-day high."
        ),
        "buy": (
            "RSI below a dynamic threshold (~40, tighter late-window); price above rising SMA-50; "
            "TA-Lib bullish reversal on current or prior bar unless RSI < 32; no chase above last sell (+3%); cooldown near last sell."
        ),
        "sell": (
            "Adaptive ATR stop (2× below SMA-21, else 2.5×), take profit at upper Bollinger when RSI > 62 "
            "(or RSI > 72), or chandelier trail on 22-day high."
        ),
    },
    "20-day breakout": {
        "style": "Donchian channel breakout",
        "summary": (
            "Turtle-style breakout: close above the prior 20-day high after a volatility squeeze. "
            "BB width percentile filter avoids late, expensive breakouts common on B3."
        ),
        "indicators": "20-day high/low (prior bar), SMA-50, BB width + 70th percentile, ATR(14), 22-day high, volume.",
        "buy": (
            "Close above yesterday’s 20-day high; price above SMA-50; BB width below its 100-bar "
            "70th percentile (squeeze); volume confirmation; cooldown near last sell."
        ),
        "sell": (
            "ATR stop-loss (2.5× ATR), chandelier trail, break below 20-day low, or "
            "two consecutive closes below breakout level (fakeout exit)."
        ),
    },
}

BENCHMARK_PERIOD = "1y"
BENCHMARK_INTERVAL = "1d"

TEST_MATRIX = [
    (algorithm, symbol)
    for algorithm in ALGORITHMS
    for symbol in BENCHMARK_SYMBOLS
]

DEFAULT_BALANCE = 10000.0
BENCHMARK_VERSION = 22

DECOMPOSITION_MODES = ("signal_only", "signal_risk", "full")
DECOMPOSITION_LABELS = {
    "signal_only": "A · Só sinal",
    "signal_risk": "B · Sinal + saídas de risco",
    "full": "C · Estratégia completa",
}
EXPECTED_TEST_COUNT = len(TEST_MATRIX)
MAX_CONCURRENT_BACKTESTS = min(10, os.cpu_count() or 4)

CACHE_DIR = Path("static/bi_cache")
DATA_PATH = CACHE_DIR / "data.json"
META_PATH = CACHE_DIR / "meta.json"
GRAPHS_DIR = CACHE_DIR / "graphs"
IBOVESPA_SERIES_PATH = CACHE_DIR / "ibovespa_series.json"
DOLLAR_SERIES_PATH = CACHE_DIR / "dollar_series.json"
REPORT_PATH = Path("static/bi_report.md")
LEGACY_RESULTS_PATH = Path("static/bi_results.json")

RESULT_FIELDS = (
    "name", "period", "interval", "period_start", "period_end", "initial_balance",
    "total_value", "gain_amount", "return_pct",
    "trade_count", "buys", "sells", "final_shares",
    "final_balance", "final_position", "vs_buy_hold_pct",
    "buy_hold_total_value", "buy_hold_gain_amount", "buy_hold_return_pct",
    "buy_hold_shares", "buy_hold_entry_price", "buy_hold_exit_price",
    "annualized_return_pct", "volatility_pct", "max_drawdown_pct", "sharpe", "sortino",
    "downside_capture_pct", "upside_capture_pct",
    "buy_hold_volatility_pct", "buy_hold_max_drawdown_pct", "buy_hold_sharpe",
    "protection_alpha_pp", "exit_attribution", "regime_returns",
    "bars_in_market", "total_bars", "exposure_pct", "experiment_mode",
    "equity_series", "drawdown_series", "buy_hold_drawdown_series", "rolling",
    "output", "graph",
)


def _is_valid_cache(meta):
    if not meta:
        return False
    if meta.get("benchmark_version") != BENCHMARK_VERSION:
        return False
    if meta.get("test_count") != EXPECTED_TEST_COUNT:
        return False
    if not DATA_PATH.exists() or not REPORT_PATH.exists():
        return False
    return True


def _load_algorithm(path):
    with open(path) as file:
        return file.read()


def _avg(rows, key, default=0.0):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return sum(vals) / len(vals) if vals else default


def summarize_algorithm_performance(results):
    by_algo = {}
    for row in results:
        if row.get("status") != "ok":
            continue
        by_algo.setdefault(row["algorithm"], []).append(row)

    performance = {}
    for name, rows in by_algo.items():
        returns = [r["return_pct"] for r in rows]
        buy_hold = [r["buy_hold_return_pct"] for r in rows]
        vs_buy_hold = [r["vs_buy_hold_pct"] for r in rows]
        vs_ibov = [r["vs_ibovespa_pct"] for r in rows]
        vs_dollar = [r["vs_dollar_pct"] for r in rows]
        best_idx = returns.index(max(returns))
        worst_idx = returns.index(min(returns))
        dd_reduction = [
            r.get("buy_hold_max_drawdown_pct", 0) - r.get("max_drawdown_pct", 0) for r in rows
        ]
        vol_reduction = [
            r.get("buy_hold_volatility_pct", 0) - r.get("volatility_pct", 0) for r in rows
        ]
        sharpe_imp = [r.get("sharpe", 0) - r.get("buy_hold_sharpe", 0) for r in rows]
        performance[name] = {
            "run_count": len(rows),
            "avg_return_pct": sum(returns) / len(returns),
            "avg_buy_hold_pct": sum(buy_hold) / len(buy_hold),
            "avg_vs_buy_hold_pct": sum(vs_buy_hold) / len(vs_buy_hold),
            "avg_vs_ibovespa_pct": sum(vs_ibov) / len(vs_ibov),
            "avg_vs_dollar_pct": sum(vs_dollar) / len(vs_dollar),
            "avg_sharpe": _avg(rows, "sharpe"),
            "avg_buy_hold_sharpe": _avg(rows, "buy_hold_sharpe"),
            "avg_max_drawdown_pct": _avg(rows, "max_drawdown_pct"),
            "avg_buy_hold_max_drawdown_pct": _avg(rows, "buy_hold_max_drawdown_pct"),
            "avg_volatility_pct": _avg(rows, "volatility_pct"),
            "avg_buy_hold_volatility_pct": _avg(rows, "buy_hold_volatility_pct"),
            "avg_downside_capture_pct": _avg(rows, "downside_capture_pct"),
            "avg_upside_capture_pct": _avg(rows, "upside_capture_pct"),
            "avg_protection_alpha_pp": _avg(rows, "protection_alpha_pp"),
            "avg_drawdown_reduction_pp": sum(dd_reduction) / len(dd_reduction),
            "avg_volatility_reduction_pp": sum(vol_reduction) / len(vol_reduction),
            "avg_sharpe_improvement": sum(sharpe_imp) / len(sharpe_imp),
            "best_return_pct": max(returns),
            "worst_return_pct": min(returns),
            "best_symbol": rows[best_idx]["symbol"],
            "worst_symbol": rows[worst_idx]["symbol"],
            "beat_buy_hold_count": sum(1 for r in rows if r["vs_buy_hold_pct"] > 0),
            "beat_ibovespa_count": sum(1 for r in rows if r["vs_ibovespa_pct"] > 0),
            "beat_dollar_count": sum(1 for r in rows if r["vs_dollar_pct"] > 0),
            "positive_runs": sum(1 for r in rows if r["gain_amount"] > 0),
            "avg_exposure_pct": _avg(rows, "exposure_pct"),
            "zero_trade_runs": sum(1 for r in rows if r.get("trade_count", 0) == 0),
            "avg_trades": _avg(rows, "trade_count"),
            "exit_attribution": aggregate_exit_attribution(rows),
            "regime_returns": {
                regime: round(sum(r.get("regime_returns", {}).get(regime, 0) for r in rows) / len(rows), 2)
                for regime in ("bull", "bear", "sideways", "high_vol")
            },
            "runs": sorted(
                [
                    {
                        "symbol": r["symbol"],
                        "name": r.get("name", ""),
                        "return_pct": r["return_pct"],
                        "buy_hold_return_pct": r["buy_hold_return_pct"],
                        "vs_buy_hold_pct": r["vs_buy_hold_pct"],
                        "vs_ibovespa_pct": r["vs_ibovespa_pct"],
                        "vs_dollar_pct": r["vs_dollar_pct"],
                        "sharpe": r.get("sharpe"),
                        "max_drawdown_pct": r.get("max_drawdown_pct"),
                        "volatility_pct": r.get("volatility_pct"),
                        "downside_capture_pct": r.get("downside_capture_pct"),
                        "protection_alpha_pp": r.get("protection_alpha_pp"),
                        "trade_count": r["trade_count"],
                        "final_position": r["final_position"],
                    }
                    for r in rows
                ],
                key=lambda item: item["symbol"],
            ),
        }
    return performance


def load_algorithm_catalog(results=None):
    performance = summarize_algorithm_performance(results or [])
    scores = risk_scores(performance)
    catalog = []
    for name, path in ALGORITHMS.items():
        perf = performance.get(name, {})
        if perf:
            perf = {**perf, "risk_score": scores.get(name, 0)}
        catalog.append({
            "name": name,
            "path": path,
            "theory": ALGORITHM_THEORY[name],
            "code": _load_algorithm(path),
            "performance": perf,
        })
    catalog.sort(key=lambda item: item.get("performance", {}).get("risk_score", 0), reverse=True)
    return catalog


def _build_summary(ok_results, ibov_return_pct, dollar_return_pct):
    return_pcts = [r["return_pct"] for r in ok_results]
    buy_hold_pcts = [r["buy_hold_return_pct"] for r in ok_results]
    vs_buy_hold = [r["vs_buy_hold_pct"] for r in ok_results]
    perf = summarize_algorithm_performance(ok_results)
    scores = risk_scores(perf)
    best_algo = max(scores, key=scores.get) if scores else ""

    return {
        "best_return_pct": max(return_pcts) if return_pcts else 0,
        "worst_return_pct": min(return_pcts) if return_pcts else 0,
        "avg_return_pct": sum(return_pcts) / len(return_pcts) if return_pcts else 0,
        "avg_buy_hold_pct": sum(buy_hold_pcts) / len(buy_hold_pcts) if buy_hold_pcts else 0,
        "ibovespa_return_pct": ibov_return_pct,
        "dollar_return_pct": dollar_return_pct,
        "avg_vs_buy_hold_pct": sum(vs_buy_hold) / len(vs_buy_hold) if vs_buy_hold else 0,
        "beat_buy_hold_count": sum(1 for r in ok_results if r["vs_buy_hold_pct"] > 0),
        "beat_ibovespa_count": sum(1 for r in ok_results if r["return_pct"] > ibov_return_pct),
        "beat_dollar_count": sum(1 for r in ok_results if r["return_pct"] > dollar_return_pct),
        "positive_runs": sum(1 for r in ok_results if r["gain_amount"] > 0),
        "avg_sharpe": _avg(ok_results, "sharpe"),
        "avg_buy_hold_sharpe": _avg(ok_results, "buy_hold_sharpe"),
        "avg_max_drawdown_pct": _avg(ok_results, "max_drawdown_pct"),
        "avg_buy_hold_max_drawdown_pct": _avg(ok_results, "buy_hold_max_drawdown_pct"),
        "avg_volatility_pct": _avg(ok_results, "volatility_pct"),
        "avg_buy_hold_volatility_pct": _avg(ok_results, "buy_hold_volatility_pct"),
        "avg_downside_capture_pct": _avg(ok_results, "downside_capture_pct"),
        "avg_upside_capture_pct": _avg(ok_results, "upside_capture_pct"),
        "avg_protection_alpha_pp": _avg(ok_results, "protection_alpha_pp"),
        "exit_attribution": aggregate_exit_attribution(ok_results),
        "best_risk_score_algo": best_algo,
        "best_risk_score": scores.get(best_algo, 0) if best_algo else 0,
        "risk_scores": scores,
        "avg_exposure_pct": _avg(ok_results, "exposure_pct"),
        "zero_trade_runs": sum(1 for r in ok_results if r.get("trade_count", 0) == 0),
        "exposure_by_algorithm": _exposure_by_algorithm(ok_results),
        "thesis": _build_thesis(ok_results),
        "conclusion": _build_conclusion(ok_results),
    }


def _exposure_by_algorithm(ok_results):
    by_algo = {}
    for row in ok_results:
        by_algo.setdefault(row["algorithm"], []).append(row)
    return {
        name: {
            "avg_exposure_pct": _avg(rows, "exposure_pct"),
            "zero_trade_runs": sum(1 for r in rows if r.get("trade_count", 0) == 0),
            "run_count": len(rows),
            "avg_trades": _avg(rows, "trade_count"),
        }
        for name, rows in by_algo.items()
    }


def _build_thesis(ok_results):
    if not ok_results:
        return "Nenhum run concluído com sucesso nesta janela do benchmark."
    avg_ret = _avg(ok_results, "return_pct")
    avg_bh = _avg(ok_results, "buy_hold_return_pct")
    avg_dd = _avg(ok_results, "max_drawdown_pct")
    avg_bh_dd = _avg(ok_results, "buy_hold_max_drawdown_pct")
    avg_exp = _avg(ok_results, "exposure_pct")
    avg_up = _avg(ok_results, "upside_capture_pct")
    avg_down = _avg(ok_results, "downside_capture_pct")
    return (
        f"As estratégias retornaram {avg_ret:.1f}% vs {avg_bh:.1f}% comprar e manter, "
        f"reduzindo o drawdown máximo de {avg_bh_dd:.1f}% para {avg_dd:.1f}%. "
        f"O tempo médio no mercado é de apenas {avg_exp:.0f}%, com "
        f"{avg_up:.0f}% de captura de alta e {avg_down:.0f}% de captura de baixa — "
        f"a redução de risco acompanha menor exposição, não participação seletiva."
    )


def _build_conclusion(ok_results):
    if not ok_results:
        return ""
    avg_exp = _avg(ok_results, "exposure_pct")
    avg_up = _avg(ok_results, "upside_capture_pct")
    return (
        "As estratégias não demonstram geração relevante de alpha versus comprar e manter, "
        "mas alcançam redução substancial de drawdown e volatilidade. "
        f"Com apenas {avg_exp:.0f}% de tempo médio no mercado e {avg_up:.0f}% de captura de alta, "
        "a maior parte da redução de risco parece vir de menor exposição ao mercado, "
        "e não de seleção de papéis ou timing superiores. "
        "Pesquisas futuras devem focar em aumentar a captura de alta (meta 50–70%) "
        "preservando a proteção na baixa (meta 20–40%)."
    )


def summarize_decomposition(rows):
    """Aggregate A/B/C experiment runs by algorithm and mode."""
    buckets = {}
    for row in rows:
        if row.get("status") != "ok":
            continue
        key = (row["algorithm"], row["experiment_mode"])
        buckets.setdefault(key, []).append(row)

    by_algorithm = {}
    for (algo, mode), runs in buckets.items():
        by_algorithm.setdefault(algo, {})[mode] = {
            "label": DECOMPOSITION_LABELS.get(mode, mode),
            "avg_return_pct": _avg(runs, "return_pct"),
            "avg_max_drawdown_pct": _avg(runs, "max_drawdown_pct"),
            "avg_exposure_pct": _avg(runs, "exposure_pct"),
            "avg_upside_capture_pct": _avg(runs, "upside_capture_pct"),
            "avg_downside_capture_pct": _avg(runs, "downside_capture_pct"),
            "avg_trades": _avg(runs, "trade_count"),
            "zero_trade_runs": sum(1 for r in runs if r.get("trade_count", 0) == 0),
        }

    for algo, modes in by_algorithm.items():
        ordered = []
        for mode in DECOMPOSITION_MODES:
            if mode in modes:
                entry = modes[mode]
                if mode == "signal_only":
                    entry["delta_return_vs_signal_pp"] = 0.0
                    entry["delta_dd_vs_signal_pp"] = 0.0
                else:
                    base = modes.get("signal_only", {})
                    entry["delta_return_vs_signal_pp"] = entry["avg_return_pct"] - base.get("avg_return_pct", 0)
                    entry["delta_dd_vs_signal_pp"] = entry["avg_max_drawdown_pct"] - base.get("avg_max_drawdown_pct", 0)
                ordered.append(entry)
        by_algorithm[algo] = ordered
    return by_algorithm


def _run_single_test(test_id, algorithm_name, symbol, algorithm_source, ibov_return_pct, dollar_return_pct):
    try:
        result = run_backtest(
            symbol=symbol,
            period=BENCHMARK_PERIOD,
            interval=BENCHMARK_INTERVAL,
            algorithm_source=algorithm_source,
            initial_balance=DEFAULT_BALANCE,
            include_graph=True,
        )
        return {
            "test_id": test_id,
            "algorithm": algorithm_name,
            "symbol": symbol,
            "status": "ok",
            "vs_ibovespa_pct": result["return_pct"] - ibov_return_pct,
            "vs_dollar_pct": result["return_pct"] - dollar_return_pct,
            **{k: result[k] for k in RESULT_FIELDS},
        }
    except Exception as exc:
        return {
            "test_id": test_id,
            "algorithm": algorithm_name,
            "symbol": symbol,
            "period": BENCHMARK_PERIOD,
            "interval": BENCHMARK_INTERVAL,
            "status": "error",
            "error": str(exc),
            "initial_balance": DEFAULT_BALANCE,
            "total_value": DEFAULT_BALANCE,
            "gain_amount": 0.0,
            "return_pct": 0.0,
            "buy_hold_return_pct": 0.0,
            "vs_buy_hold_pct": 0.0,
            "vs_ibovespa_pct": 0.0,
            "vs_dollar_pct": 0.0,
            "trade_count": 0,
            "buys": 0,
            "sells": 0,
            "final_shares": 0,
            "final_balance": DEFAULT_BALANCE,
            "final_position": "Neutral",
            "output": [],
        }


async def _run_single_test_async(
    test_id,
    algorithm_name,
    symbol,
    algorithm_source,
    ibov_return_pct,
    dollar_return_pct,
    semaphore,
):
    async with semaphore:
        return await asyncio.to_thread(
            _run_single_test,
            test_id,
            algorithm_name,
            symbol,
            algorithm_source,
            ibov_return_pct,
            dollar_return_pct,
        )


def _run_decomposition_test(algorithm_name, symbol, algorithm_source, mode, ibov_return_pct, dollar_return_pct):
    try:
        result = run_backtest(
            symbol=symbol,
            period=BENCHMARK_PERIOD,
            interval=BENCHMARK_INTERVAL,
            algorithm_source=algorithm_source,
            initial_balance=DEFAULT_BALANCE,
            include_graph=False,
            experiment_mode=mode,
        )
        return {
            "algorithm": algorithm_name,
            "symbol": symbol,
            "experiment_mode": mode,
            "status": "ok",
            **{k: result[k] for k in RESULT_FIELDS if k in result},
        }
    except Exception as exc:
        return {
            "algorithm": algorithm_name,
            "symbol": symbol,
            "experiment_mode": mode,
            "status": "error",
            "error": str(exc),
        }


async def _run_decomposition_async(algorithm_name, symbol, algorithm_source, mode, ibov_return_pct, dollar_return_pct, semaphore):
    async with semaphore:
        return await asyncio.to_thread(
            _run_decomposition_test,
            algorithm_name,
            symbol,
            algorithm_source,
            mode,
            ibov_return_pct,
            dollar_return_pct,
        )


async def run_bi_suite():
    algorithm_sources = {name: _load_algorithm(path) for name, path in ALGORITHMS.items()}

    market_benchmark, dollar_bench = await asyncio.gather(
        asyncio.to_thread(
            ibovespa_benchmark,
            BENCHMARK_PERIOD,
            BENCHMARK_INTERVAL,
            DEFAULT_BALANCE,
        ),
        asyncio.to_thread(
            dollar_benchmark,
            BENCHMARK_PERIOD,
            BENCHMARK_INTERVAL,
            DEFAULT_BALANCE,
        ),
    )
    ibov_return_pct = market_benchmark["buy_hold_return_pct"]
    dollar_return_pct = dollar_bench["buy_hold_return_pct"]

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_BACKTESTS)
    tasks = [
        _run_single_test_async(
            test_id,
            algorithm_name,
            symbol,
            algorithm_sources[algorithm_name],
            ibov_return_pct,
            dollar_return_pct,
            semaphore,
        )
        for test_id, (algorithm_name, symbol) in enumerate(TEST_MATRIX, start=1)
    ]
    results = list(await asyncio.gather(*tasks))
    results.sort(key=lambda row: row["test_id"])

    ok_results = [r for r in results if r["status"] == "ok"]

    decomp_tasks = [
        _run_decomposition_async(
            algorithm_name,
            symbol,
            algorithm_sources[algorithm_name],
            mode,
            ibov_return_pct,
            dollar_return_pct,
            semaphore,
        )
        for algorithm_name in ALGORITHMS
        for symbol in BENCHMARK_SYMBOLS
        for mode in DECOMPOSITION_MODES
    ]
    decomposition_runs = list(await asyncio.gather(*decomp_tasks))
    decomposition = summarize_decomposition(decomposition_runs)

    summary = _build_summary(ok_results, ibov_return_pct, dollar_return_pct)
    summary["decomposition"] = decomposition

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "market": "B3 (Bovespa)",
        "scenario": (
            f"B3 · 5 algoritmos × {len(BENCHMARK_SYMBOLS)} papéis · "
            f"{BENCHMARK_PERIOD} / {BENCHMARK_INTERVAL} · "
            f"saldo inicial R$ {DEFAULT_BALANCE:,.0f}"
        ),
        "test_count": len(results),
        "algorithm_count": len(ALGORITHMS),
        "stock_count": len(BENCHMARK_SYMBOLS),
        "period": BENCHMARK_PERIOD,
        "interval": BENCHMARK_INTERVAL,
        "market_benchmark": market_benchmark,
        "dollar_benchmark": dollar_bench,
        "summary": summary,
        "decomposition": decomposition,
        "results": results,
    }


def _slim_benchmark(benchmark):
    slim = copy.deepcopy(benchmark)
    slim.pop("normalized_series", None)
    return slim


def _write_cache(payload):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)

    for old_graph in GRAPHS_DIR.glob("*.json"):
        old_graph.unlink()

    slim_results = []
    for row in payload["results"]:
        slim_row = {k: v for k, v in row.items() if k not in ("graph", "equity_series", "rolling")}
        graph = row.get("graph")
        if graph:
            graph_path = GRAPHS_DIR / f"{row['test_id']}.json"
            with open(graph_path, "w") as file:
                json.dump(graph, file)
            slim_row["graph_path"] = str(graph_path)
        if row.get("drawdown_series"):
            dd_path = GRAPHS_DIR / f"{row['test_id']}_dd.json"
            with open(dd_path, "w") as file:
                json.dump(
                    {
                        "strategy": row.get("drawdown_series", []),
                        "buy_hold": row.get("buy_hold_drawdown_series", []),
                        "rolling": row.get("rolling", {}),
                    },
                    file,
                )
            slim_row["drawdown_path"] = str(dd_path)
        slim_results.append(slim_row)

    slim_payload = {
        **{k: v for k, v in payload.items() if k not in ("results", "market_benchmark", "dollar_benchmark")},
        "market_benchmark": _slim_benchmark(payload["market_benchmark"]),
        "dollar_benchmark": _slim_benchmark(payload["dollar_benchmark"]),
        "results": slim_results,
    }

    with open(DATA_PATH, "w") as file:
        json.dump(slim_payload, file, indent=2)

    with open(IBOVESPA_SERIES_PATH, "w") as file:
        json.dump(payload["market_benchmark"].get("normalized_series", []), file)

    with open(DOLLAR_SERIES_PATH, "w") as file:
        json.dump(payload["dollar_benchmark"].get("normalized_series", []), file)

    meta = {
        "benchmark_version": payload["benchmark_version"],
        "generated_at": payload["generated_at"],
        "test_count": payload["test_count"],
        "report_path": str(REPORT_PATH),
    }
    with open(META_PATH, "w") as file:
        json.dump(meta, file, indent=2)

    write_markdown(payload, REPORT_PATH, algorithm_catalog=load_algorithm_catalog(payload["results"]))

    # Legacy single-file cache for compatibility
    with open(LEGACY_RESULTS_PATH, "w") as file:
        json.dump(payload, file)


def _hydrate_cache(data):
    payload = copy.deepcopy(data)

    if IBOVESPA_SERIES_PATH.exists():
        with open(IBOVESPA_SERIES_PATH) as file:
            payload.setdefault("market_benchmark", {})["normalized_series"] = json.load(file)

    if DOLLAR_SERIES_PATH.exists():
        with open(DOLLAR_SERIES_PATH) as file:
            payload.setdefault("dollar_benchmark", {})["normalized_series"] = json.load(file)

    for row in payload.get("results", []):
        graph_path = row.pop("graph_path", None)
        if graph_path and Path(graph_path).exists() and Path(graph_path).stat().st_size > 0:
            with open(graph_path) as file:
                row["graph"] = json.load(file)
        dd_path = row.pop("drawdown_path", None)
        if dd_path and Path(dd_path).exists() and Path(dd_path).stat().st_size > 0:
            with open(dd_path) as file:
                dd_data = json.load(file)
            row["drawdown_series"] = dd_data.get("strategy", [])
            row["buy_hold_drawdown_series"] = dd_data.get("buy_hold", [])
            row["rolling"] = dd_data.get("rolling", {})

    return payload


async def save_bi_results_async():
    payload = await run_bi_suite()
    _write_cache(payload)
    return payload


def save_bi_results():
    return asyncio.run(save_bi_results_async())


def load_bi_results(force_refresh=False):
    if force_refresh:
        return save_bi_results()

    meta = None
    if META_PATH.exists():
        with open(META_PATH) as file:
            meta = json.load(file)

    if _is_valid_cache(meta):
        with open(DATA_PATH) as file:
            data = json.load(file)
        return _hydrate_cache(data)

    if LEGACY_RESULTS_PATH.exists():
        with open(LEGACY_RESULTS_PATH) as file:
            legacy = json.load(file)
        if legacy.get("benchmark_version") == BENCHMARK_VERSION and legacy.get("test_count") == EXPECTED_TEST_COUNT:
            _write_cache(legacy)
            return legacy

    return save_bi_results()


if __name__ == "__main__":
    data = save_bi_results()
    print(f"Cached {data['test_count']} tests to {CACHE_DIR}")
    print(f"Markdown report: {REPORT_PATH}")
