"""Risk-adjusted performance metrics for backtest equity curves."""

import math
from statistics import mean, pstdev

TRADING_DAYS = 252

EXIT_ENGINE = {
    "ATR stop": "risk",
    "Chandelier trail": "risk",
    "SMA break": "signal",
    "SMA-50 break": "signal",
    "Bearish cross": "signal",
    "RSI take profit": "signal",
    "RSI overbought": "signal",
    "Break below 20d low": "signal",
    "Fakeout exit": "signal",
    "Bollinger take profit": "signal",
}


def exit_engine(reason):
    return EXIT_ENGINE.get(reason, "signal")


def buy_hold_equity_series(raw_df, initial_balance):
    """Mark-to-market buy & hold on the same bar index as the strategy loop."""
    if raw_df.empty:
        return []
    entry_price = float(raw_df["Close"].iloc[0])
    if entry_price <= 0:
        return []
    shares = initial_balance / entry_price
    cash = 0.0
    series = []
    for idx, row in raw_df.iterrows():
        price = float(row["Close"])
        equity = cash + shares * price
        series.append({"date": idx.isoformat(), "equity": equity})
    return series


def daily_returns(equity_series):
    if len(equity_series) < 2:
        return []
    out = []
    for i in range(1, len(equity_series)):
        prev = equity_series[i - 1]["equity"]
        curr = equity_series[i]["equity"]
        if prev > 0:
            out.append((equity_series[i]["date"], (curr / prev) - 1.0))
    return out


def drawdown_series(equity_series):
    if not equity_series:
        return []
    peak = equity_series[0]["equity"]
    out = []
    for point in equity_series:
        eq = point["equity"]
        if eq > peak:
            peak = eq
        dd_pct = ((eq - peak) / peak * 100) if peak else 0.0
        out.append({**point, "drawdown_pct": dd_pct})
    return out


def max_drawdown_pct(equity_series):
    series = drawdown_series(equity_series)
    if not series:
        return 0.0
    return abs(min(point["drawdown_pct"] for point in series))


def annualized_return_pct(equity_series):
    if len(equity_series) < 2:
        return 0.0
    start = equity_series[0]["equity"]
    end = equity_series[-1]["equity"]
    n_days = len(equity_series) - 1
    if start <= 0 or n_days <= 0:
        return 0.0
    total = end / start
    return (total ** (TRADING_DAYS / n_days) - 1.0) * 100


def volatility_pct(returns):
    if len(returns) < 2:
        return 0.0
    vals = [r for _, r in returns]
    return pstdev(vals) * math.sqrt(TRADING_DAYS) * 100


def sharpe_ratio(ann_return_pct, vol_pct, risk_free_pct=0.0):
    if vol_pct <= 0:
        return 0.0
    return (ann_return_pct - risk_free_pct) / vol_pct


def sortino_ratio(ann_return_pct, returns, risk_free_pct=0.0):
    downside = [min(0.0, r) for _, r in returns]
    if not downside:
        return 0.0
    down_dev = pstdev(downside) * math.sqrt(TRADING_DAYS) * 100 if len(downside) > 1 else 0.0
    if down_dev <= 0:
        return 0.0
    return (ann_return_pct - risk_free_pct) / down_dev


def _aligned_returns(strategy_returns, benchmark_returns):
    bench = {d: r for d, r in benchmark_returns}
    s_vals, b_vals = [], []
    for d, r in strategy_returns:
        if d in bench:
            s_vals.append(r)
            b_vals.append(bench[d])
    return s_vals, b_vals


def capture_ratio(strategy_returns, benchmark_returns, direction):
    s_vals, b_vals = _aligned_returns(strategy_returns, benchmark_returns)
    if not s_vals:
        return None
    if direction == "down":
        pairs = [(s, b) for s, b in zip(s_vals, b_vals) if b < 0]
    else:
        pairs = [(s, b) for s, b in zip(s_vals, b_vals) if b > 0]
    if not pairs:
        return None
    strat_mean = mean(s for s, _ in pairs) * 100
    bench_mean = mean(b for _, b in pairs) * 100
    if bench_mean == 0:
        return None
    return (strat_mean / bench_mean) * 100


def protection_alpha_pp(strategy_metrics, benchmark_metrics):
    return_sacrifice = max(0.0, benchmark_metrics["return_pct"] - strategy_metrics["return_pct"])
    dd_reduction = benchmark_metrics["max_drawdown_pct"] - strategy_metrics["max_drawdown_pct"]
    vol_reduction = benchmark_metrics["volatility_pct"] - strategy_metrics["volatility_pct"]
    return dd_reduction + vol_reduction - return_sacrifice


def rolling_windows(equity_series, windows=(30, 90)):
    returns = daily_returns(equity_series)
    if not returns:
        return {}
    out = {}
    for window in windows:
        roll_ret, roll_sharpe = [], []
        dates = [d for d, _ in returns]
        vals = [r for _, r in returns]
        for i in range(window, len(vals) + 1):
            chunk = vals[i - window : i]
            cum = 1.0
            for r in chunk:
                cum *= 1.0 + r
            period_ret = (cum - 1.0) * 100
            vol = pstdev(chunk) * math.sqrt(TRADING_DAYS) * 100 if len(chunk) > 1 else 0.0
            ann = ((1.0 + period_ret / 100) ** (TRADING_DAYS / window) - 1.0) * 100
            sh = sharpe_ratio(ann, vol)
            roll_ret.append({"date": dates[i - 1], "value": period_ret})
            roll_sharpe.append({"date": dates[i - 1], "value": sh})
        out[str(window)] = {"return": roll_ret, "sharpe": roll_sharpe}
    return out


def classify_regime(row, atr_p70):
    close = float(row["Close"])
    sma50 = float(row.get("sma50", close))
    slope = float(row.get("sma50_slope", 0.0))
    atr = float(row.get("atr14", 0.0))
    if atr_p70 and atr >= atr_p70:
        return "high_vol"
    if close > sma50 and slope > 0:
        return "bull"
    if close < sma50 and slope < 0:
        return "bear"
    return "sideways"


def regime_returns(equity_series, regime_df):
    """Attribute daily strategy returns to bull/bear/sideways/high_vol buckets."""
    returns = daily_returns(equity_series)
    if not returns:
        return {}

    regime_lookup = {}
    atr_vals = regime_df["atr14"].tolist() if "atr14" in regime_df.columns else []
    atr_p70 = sorted(atr_vals)[int(len(atr_vals) * 0.7)] if len(atr_vals) > 10 else None

    for idx, row in regime_df.iterrows():
        regime_lookup[idx.isoformat()] = classify_regime(row, atr_p70)

    buckets = {k: [] for k in ("bull", "bear", "sideways", "high_vol")}
    for d, r in returns:
        regime = regime_lookup.get(d, "sideways")
        buckets[regime].append(r)

    def _ann(bucket):
        if not bucket:
            return 0.0
        avg_daily = mean(bucket)
        return ((1.0 + avg_daily) ** TRADING_DAYS - 1.0) * 100

    return {k: round(_ann(v), 2) for k, v in buckets.items()}


def compute_risk_metrics(strategy_equity, benchmark_equity, terminal_return_pct):
    s_ret = daily_returns(strategy_equity)
    b_ret = daily_returns(benchmark_equity)
    ann = annualized_return_pct(strategy_equity)
    vol = volatility_pct(s_ret)
    mdd = max_drawdown_pct(strategy_equity)
    sh = sharpe_ratio(ann, vol)
    so = sortino_ratio(ann, s_ret)
    down_cap = capture_ratio(s_ret, b_ret, "down")
    up_cap = capture_ratio(s_ret, b_ret, "up")

    bench_ann = annualized_return_pct(benchmark_equity)
    bench_vol = volatility_pct(b_ret)
    bench_mdd = max_drawdown_pct(benchmark_equity)
    bench_sh = sharpe_ratio(bench_ann, bench_vol)

    strat = {
        "return_pct": terminal_return_pct,
        "annualized_return_pct": ann,
        "volatility_pct": vol,
        "max_drawdown_pct": mdd,
        "sharpe": sh,
        "sortino": so,
    }
    bench = {
        "return_pct": ((benchmark_equity[-1]["equity"] / benchmark_equity[0]["equity"]) - 1) * 100
        if len(benchmark_equity) > 1 and benchmark_equity[0]["equity"] > 0
        else 0.0,
        "volatility_pct": bench_vol,
        "max_drawdown_pct": bench_mdd,
        "sharpe": bench_sh,
    }

    return {
        "annualized_return_pct": round(ann, 2),
        "volatility_pct": round(vol, 2),
        "max_drawdown_pct": round(mdd, 2),
        "sharpe": round(sh, 2),
        "sortino": round(so, 2),
        "downside_capture_pct": round(down_cap, 1) if down_cap is not None else None,
        "upside_capture_pct": round(up_cap, 1) if up_cap is not None else None,
        "buy_hold_volatility_pct": round(bench_vol, 2),
        "buy_hold_max_drawdown_pct": round(bench_mdd, 2),
        "buy_hold_sharpe": round(bench_sh, 2),
        "protection_alpha_pp": round(protection_alpha_pp(strat, bench), 2),
        "drawdown_series": drawdown_series(strategy_equity),
        "buy_hold_drawdown_series": drawdown_series(benchmark_equity),
        "rolling": rolling_windows(strategy_equity),
    }


def risk_scores(algorithm_metrics):
    """Rank algorithms 0–100 from drawdown/vol reduction and Sharpe improvement."""
    if not algorithm_metrics:
        return {}

    dd_reds, vol_reds, sharpe_imps = [], [], []
    for m in algorithm_metrics.values():
        dd_reds.append(m.get("avg_drawdown_reduction_pp", 0))
        vol_reds.append(m.get("avg_volatility_reduction_pp", 0))
        sharpe_imps.append(m.get("avg_sharpe_improvement", 0))

    def _norm(vals, v):
        lo, hi = min(vals), max(vals)
        if hi == lo:
            return 50.0
        return (v - lo) / (hi - lo) * 100

    scores = {}
    for name, m in algorithm_metrics.items():
        dd_n = _norm(dd_reds, m.get("avg_drawdown_reduction_pp", 0))
        vol_n = _norm(vol_reds, m.get("avg_volatility_reduction_pp", 0))
        sh_n = _norm(sharpe_imps, m.get("avg_sharpe_improvement", 0))
        score = 0.4 * dd_n + 0.3 * vol_n + 0.3 * sh_n
        scores[name] = round(score, 1)
    return scores


def aggregate_exit_attribution(runs):
    totals = {}
    engine_totals = {"signal": 0.0, "risk": 0.0}
    for run in runs:
        for reason, pnl_pct in (run.get("exit_attribution") or {}).items():
            totals[reason] = totals.get(reason, 0.0) + pnl_pct
            engine = exit_engine(reason)
            engine_totals[engine] += pnl_pct
    count = len(runs) or 1
    return {
        "by_reason": {k: round(v / count, 3) for k, v in sorted(totals.items(), key=lambda x: -x[1])},
        "by_engine": {k: round(v / count, 3) for k, v in engine_totals.items()},
    }
