"""Shared helpers injected into user algorithm code."""

import numpy as np

BULLISH_REVERSAL_PATTERNS = (
    "CDLHAMMER",
    "CDLINVERTEDHAMMER",
    "CDLENGULFING",
    "CDLMORNINGSTAR",
    "CDLPIERCING",
    "CDLHARAMI",
)

BEARISH_REVERSAL_PATTERNS = (
    "CDLSHOOTINGSTAR",
    "CDLENGULFING",
    "CDLEVENINGSTAR",
    "CDLHANGINGMAN",
    "CDLDARKCLOUDCOVER",
)


def entry_reluctance_y(progress):
    """After 75% of the period, linear reluctance y = x + 2 (x over the final 25%)."""
    if progress <= 0.75:
        return 1.0
    x = (progress - 0.75) / 0.25
    return x + 2.0


def update_time_state(portfolio, bar_index, total_bars):
    progress = bar_index / total_bars if total_bars else 1.0
    portfolio["_bar_index"] = bar_index
    portfolio["_period_progress"] = progress
    portfolio["_entry_reluctance"] = entry_reluctance_y(progress)


RISK_EXIT_LABELS = frozenset({"ATR stop", "Chandelier trail"})


def experiment_mode(portfolio):
    return portfolio.get("_experiment_mode", "full")


def entry_filters_active(portfolio):
    """Cooldown, chase limits, extension caps — disabled in signal_only / signal_risk."""
    return experiment_mode(portfolio) == "full"


def first_sell_reason(checks, portfolio=None):
    """Return the label of the first fired sell condition, or None."""
    if portfolio and experiment_mode(portfolio) == "signal_only":
        checks = [(label, fired) for label, fired in checks if label not in RISK_EXIT_LABELS]
    for label, fired in checks:
        if fired:
            return label
    return None


def entry_gate(allowed, portfolio):
    """Apply reluctant-entry gating only in full (production) mode."""
    if not allowed:
        return False
    if experiment_mode(portfolio) in ("signal_only", "signal_risk"):
        return True
    return reluctant_entry(True, portfolio)


def reluctant_entry(allowed, portfolio):
    """Gate entries in the last 25% of the window; higher y = more reluctant."""
    if not allowed:
        return False
    if experiment_mode(portfolio) in ("signal_only", "signal_risk"):
        return True
    y = portfolio.get("_entry_reluctance", 1.0)
    if y <= 1.0:
        return True
    x = y - 2.0
    appetite = 1.0 - x
    bar = portfolio.get("_bar_index", 0)
    phase = (bar % 97) / 97.0
    return phase < appetite


def _ohlc_arrays(df):
    return (
        df["Open"].values,
        df["High"].values,
        df["Low"].values,
        df["Close"].values,
    )


def add_bullish_reversal_column(df, column="bullish_reversal"):
    """TA-Lib CDL* bullish reversal composite (1 = pattern on bar)."""
    import talib

    o, h, l, c = _ohlc_arrays(df)
    signals = [getattr(talib, name)(o, h, l, c) for name in BULLISH_REVERSAL_PATTERNS]
    df[column] = (np.max(signals, axis=0) > 0).astype(int)
    return df


def add_bearish_reversal_column(df, column="bearish_reversal"):
    """TA-Lib CDL* bearish reversal composite (1 = pattern on bar)."""
    import talib

    o, h, l, c = _ohlc_arrays(df)
    signals = [getattr(talib, name)(o, h, l, c) for name in BEARISH_REVERSAL_PATTERNS]
    df[column] = (np.min(signals, axis=0) < 0).astype(int)
    return df


def inject_algorithm_helpers(namespace):
    namespace["reluctant_entry"] = reluctant_entry
    namespace["entry_gate"] = entry_gate
    namespace["entry_filters_active"] = entry_filters_active
    namespace["first_sell_reason"] = first_sell_reason
    namespace["add_bullish_reversal_column"] = add_bullish_reversal_column
    namespace["add_bearish_reversal_column"] = add_bearish_reversal_column


def exec_user_algorithm(algorithm_source, namespace=None):
    """Exec user algorithm with helpers visible inside defined functions."""
    if namespace is None:
        namespace = {}
    namespace["__builtins__"] = __builtins__
    inject_algorithm_helpers(namespace)

    source = algorithm_source
    prefix = []
    if "reluctant_entry" in source and "def reluctant_entry" not in source:
        if "from algorithm_helpers import reluctant_entry" not in source:
            prefix.append("from algorithm_helpers import reluctant_entry")
    if "add_bullish_reversal_column" in source and "def add_bullish_reversal_column" not in source:
        if "add_bullish_reversal_column" not in source.split("import", 1)[0]:
            prefix.append("from algorithm_helpers import add_bullish_reversal_column")
    if "first_sell_reason" in source and "def first_sell_reason" not in source:
        if "first_sell_reason" not in source.split("import", 1)[0]:
            prefix.append("from algorithm_helpers import first_sell_reason")
    if "entry_gate" in source and "def entry_gate" not in source:
        if "entry_gate" not in source.split("import", 1)[0]:
            prefix.append("from algorithm_helpers import entry_gate, entry_filters_active")
    if prefix:
        source = "\n".join(prefix) + "\n" + source

    exec(compile(source, "<user_algorithm>", "exec"), namespace, namespace)
    return namespace
