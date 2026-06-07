import json
import copy
from datetime import datetime, timezone
from pathlib import Path

from benchmarks import dollar_benchmark, ibovespa_benchmark
from bi_report import write_markdown
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
        "indicators": "SMA-8, SMA-21, SMA-50, 5-bar SMA-8 slope, ATR(14), 22-day high.",
        "buy": (
            "Price above SMA-8 with a positive slope; price above SMA-21 and SMA-50; "
            "not more than ~3.5% extended above SMA-8; avoids re-buying immediately after a recent sell. "
            "Uses reluctant entry to skip marginal signals after losses."
        ),
        "sell": (
            "ATR stop-loss (3× ATR below entry), chandelier trail (22-day high − 2.5× ATR), "
            "or close below SMA-21 once the trade is profitable after commission."
        ),
    },
    "SMA-20 trend": {
        "style": "Medium-term trend following",
        "summary": (
            "A slower cousin of the SMA-8 strategy. The 20-day average filters out more noise "
            "and targets sustained moves where medium- and long-term trends align."
        ),
        "indicators": "SMA-20, SMA-50, 5-bar SMA-20 slope, ATR(14), 22-day high.",
        "buy": (
            "Price above SMA-20 with rising slope; SMA-20 above SMA-50; price near SMA-50 support; "
            "not chasing more than ~4% above SMA-20; cooldown after recent sells."
        ),
        "sell": (
            "ATR stop-loss (3× ATR), chandelier trail, or break below SMA-50 when profitable."
        ),
    },
    "SMA crossover": {
        "style": "Dual moving-average crossover",
        "summary": (
            "A well-known momentum signal: when a fast average crosses above a slow one, "
            "momentum may be shifting bullish. This version requires the broader uptrend "
            "(price above SMA-50) and volume confirmation."
        ),
        "indicators": "SMA-8, SMA-21, SMA-50, ATR(14), 22-day high, 20-day average volume.",
        "buy": (
            "Fresh bullish cross — SMA-8 just crossed above SMA-21 on the current bar; "
            "price above SMA-50; volume at least ~85% of its 20-day average."
        ),
        "sell": (
            "ATR stop-loss, chandelier trail, or bearish cross (SMA-8 below SMA-21) once profitable."
        ),
    },
    "RSI reversion": {
        "style": "Mean reversion in an uptrend",
        "summary": (
            "Buys short-term pullbacks in stocks that are still in a longer uptrend. "
            "RSI measures how stretched price is; low RSI after a dip can signal a bounce — "
            "but only when the 50-day trend is still intact."
        ),
        "indicators": "RSI(14), SMA-50 and its slope, ATR(14), 10-day high.",
        "buy": (
            "RSI below a dynamic threshold (stricter after losing streaks); price above rising SMA-50; "
            "RSI not in panic territory (< 25); avoids immediate re-entry near the last sell price."
        ),
        "sell": (
            "ATR stop-loss (2.5× ATR), take profit when RSI > 65, or chandelier trail on 10-day high."
        ),
    },
    "20-day breakout": {
        "style": "Donchian channel breakout",
        "summary": (
            "Inspired by turtle-style breakout systems: when price closes above the highest high "
            "of the prior 20 sessions, it may be starting a new leg up. A long-term filter and "
            "volume gate reduce false breaks."
        ),
        "indicators": "20-day high/low (prior bar), SMA-50, ATR(14), 22-day high, 20-day average volume.",
        "buy": (
            "Close above yesterday’s 20-day high; price above SMA-50; volume above ~110% of average "
            "(threshold rises after losses); cooldown near last sell."
        ),
        "sell": (
            "ATR stop-loss (2.5× ATR), chandelier trail, or close below the 20-day low when profitable."
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
BENCHMARK_VERSION = 9
EXPECTED_TEST_COUNT = len(TEST_MATRIX)

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
        performance[name] = {
            "run_count": len(rows),
            "avg_return_pct": sum(returns) / len(returns),
            "avg_buy_hold_pct": sum(buy_hold) / len(buy_hold),
            "avg_vs_buy_hold_pct": sum(vs_buy_hold) / len(vs_buy_hold),
            "avg_vs_ibovespa_pct": sum(vs_ibov) / len(vs_ibov),
            "avg_vs_dollar_pct": sum(vs_dollar) / len(vs_dollar),
            "best_return_pct": max(returns),
            "worst_return_pct": min(returns),
            "best_symbol": rows[best_idx]["symbol"],
            "worst_symbol": rows[worst_idx]["symbol"],
            "beat_buy_hold_count": sum(1 for r in rows if r["vs_buy_hold_pct"] > 0),
            "beat_ibovespa_count": sum(1 for r in rows if r["vs_ibovespa_pct"] > 0),
            "beat_dollar_count": sum(1 for r in rows if r["vs_dollar_pct"] > 0),
            "positive_runs": sum(1 for r in rows if r["gain_amount"] > 0),
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
    catalog = []
    for name, path in ALGORITHMS.items():
        catalog.append({
            "name": name,
            "path": path,
            "theory": ALGORITHM_THEORY[name],
            "code": _load_algorithm(path),
            "performance": performance.get(name, {}),
        })
    return catalog


def _build_summary(ok_results, ibov_return_pct, dollar_return_pct):
    return_pcts = [r["return_pct"] for r in ok_results]
    buy_hold_pcts = [r["buy_hold_return_pct"] for r in ok_results]
    vs_buy_hold = [r["vs_buy_hold_pct"] for r in ok_results]

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
    }


def run_bi_suite():
    market_benchmark = ibovespa_benchmark(
        BENCHMARK_PERIOD, BENCHMARK_INTERVAL, DEFAULT_BALANCE
    )
    dollar_bench = dollar_benchmark(
        BENCHMARK_PERIOD, BENCHMARK_INTERVAL, DEFAULT_BALANCE
    )
    ibov_return_pct = market_benchmark["buy_hold_return_pct"]
    dollar_return_pct = dollar_bench["buy_hold_return_pct"]

    results = []
    for test_id, (algorithm_name, symbol) in enumerate(TEST_MATRIX, start=1):
        algorithm_path = ALGORITHMS[algorithm_name]
        try:
            result = run_backtest(
                symbol=symbol,
                period=BENCHMARK_PERIOD,
                interval=BENCHMARK_INTERVAL,
                algorithm_source=_load_algorithm(algorithm_path),
                initial_balance=DEFAULT_BALANCE,
                include_graph=True,
            )
            results.append(
                {
                    "test_id": test_id,
                    "algorithm": algorithm_name,
                    "symbol": symbol,
                    "status": "ok",
                    "vs_ibovespa_pct": result["return_pct"] - ibov_return_pct,
                    "vs_dollar_pct": result["return_pct"] - dollar_return_pct,
                    **{k: result[k] for k in RESULT_FIELDS},
                }
            )
        except Exception as exc:
            results.append(
                {
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
            )

    ok_results = [r for r in results if r["status"] == "ok"]

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "market": "B3 (Bovespa)",
        "scenario": (
            f"B3 · 5 algorithms × {len(BENCHMARK_SYMBOLS)} stocks · "
            f"{BENCHMARK_PERIOD} / {BENCHMARK_INTERVAL} · "
            f"R$ {DEFAULT_BALANCE:,.0f} starting balance"
        ),
        "test_count": len(results),
        "algorithm_count": len(ALGORITHMS),
        "stock_count": len(BENCHMARK_SYMBOLS),
        "period": BENCHMARK_PERIOD,
        "interval": BENCHMARK_INTERVAL,
        "market_benchmark": market_benchmark,
        "dollar_benchmark": dollar_bench,
        "summary": _build_summary(ok_results, ibov_return_pct, dollar_return_pct),
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
        slim_row = {k: v for k, v in row.items() if k != "graph"}
        graph = row.get("graph")
        if graph:
            graph_path = GRAPHS_DIR / f"{row['test_id']}.json"
            with open(graph_path, "w") as file:
                json.dump(graph, file)
            slim_row["graph_path"] = str(graph_path)
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
        if graph_path and Path(graph_path).exists():
            with open(graph_path) as file:
                row["graph"] = json.load(file)

    return payload


def save_bi_results():
    payload = run_bi_suite()
    _write_cache(payload)
    return payload


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
