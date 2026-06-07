import json
from datetime import datetime, timezone
from pathlib import Path

from simulator import run_backtest

ALGORITHMS = {
    "SMA-8 trend": "algorithms/sma8_trend.py",
    "SMA-20 trend": "algorithms/sma20_trend.py",
    "SMA crossover": "algorithms/sma_crossover.py",
    "RSI reversion": "algorithms/rsi_reversion.py",
    "20-day breakout": "algorithms/breakout_20d.py",
}

TEST_MATRIX = [
    ("SMA-8 trend", "AAPL"),
    ("SMA-8 trend", "MSFT"),
    ("SMA-20 trend", "AAPL"),
    ("SMA-20 trend", "MSFT"),
    ("SMA crossover", "AAPL"),
    ("SMA crossover", "MSFT"),
    ("RSI reversion", "AAPL"),
    ("RSI reversion", "MSFT"),
    ("20-day breakout", "AAPL"),
    ("20-day breakout", "MSFT"),
]

DEFAULT_PERIOD = "1y"
DEFAULT_INTERVAL = "1d"
DEFAULT_BALANCE = 10000.0
RESULTS_PATH = Path("static/bi_results.json")


def _load_algorithm(path):
    with open(path) as file:
        return file.read()


def run_bi_suite():
    results = []
    for test_id, (algorithm_name, symbol) in enumerate(TEST_MATRIX, start=1):
        algorithm_path = ALGORITHMS[algorithm_name]
        try:
            result = run_backtest(
                symbol=symbol,
                period=DEFAULT_PERIOD,
                interval=DEFAULT_INTERVAL,
                algorithm_source=_load_algorithm(algorithm_path),
                initial_balance=DEFAULT_BALANCE,
            )
            results.append(
                {
                    "test_id": test_id,
                    "algorithm": algorithm_name,
                    "symbol": symbol,
                    "status": "ok",
                    **{k: result[k] for k in (
                        "name", "period", "interval", "initial_balance",
                        "total_value", "gain_amount", "return_pct",
                        "trade_count", "buys", "sells",
                    )},
                }
            )
        except Exception as exc:
            results.append(
                {
                    "test_id": test_id,
                    "algorithm": algorithm_name,
                    "symbol": symbol,
                    "status": "error",
                    "error": str(exc),
                    "initial_balance": DEFAULT_BALANCE,
                    "total_value": DEFAULT_BALANCE,
                    "gain_amount": 0.0,
                    "return_pct": 0.0,
                    "trade_count": 0,
                    "buys": 0,
                    "sells": 0,
                }
            )

    ok_results = [r for r in results if r["status"] == "ok"]
    return_pcts = [r["return_pct"] for r in ok_results]

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "scenario": f"{DEFAULT_PERIOD} / {DEFAULT_INTERVAL} · ${DEFAULT_BALANCE:,.0f} starting balance",
        "test_count": len(results),
        "algorithm_count": len(ALGORITHMS),
        "summary": {
            "best_return_pct": max(return_pcts) if return_pcts else 0,
            "worst_return_pct": min(return_pcts) if return_pcts else 0,
            "avg_return_pct": sum(return_pcts) / len(return_pcts) if return_pcts else 0,
            "positive_runs": sum(1 for r in ok_results if r["gain_amount"] > 0),
        },
        "results": results,
    }
    return payload


def save_bi_results(path=RESULTS_PATH):
    payload = run_bi_suite()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as file:
        json.dump(payload, file, indent=2)
    return payload


def load_bi_results(path=RESULTS_PATH):
    if not path.exists():
        return save_bi_results(path)
    with open(path) as file:
        return json.load(file)


if __name__ == "__main__":
    data = save_bi_results()
    print(f"Saved {data['test_count']} tests to {RESULTS_PATH}")
