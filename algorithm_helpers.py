"""Shared helpers injected into user algorithm code."""


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


def reluctant_entry(allowed, portfolio):
    """Gate entries in the last 25% of the window; higher y = more reluctant."""
    if not allowed:
        return False
    y = portfolio.get("_entry_reluctance", 1.0)
    if y <= 1.0:
        return True
    x = y - 2.0
    appetite = 1.0 - x
    bar = portfolio.get("_bar_index", 0)
    phase = (bar % 97) / 97.0
    return phase < appetite


def inject_algorithm_helpers(namespace):
    namespace["reluctant_entry"] = reluctant_entry


def exec_user_algorithm(algorithm_source, namespace=None):
    """Exec user algorithm with helpers visible inside defined functions."""
    if namespace is None:
        namespace = {}
    namespace["__builtins__"] = __builtins__
    inject_algorithm_helpers(namespace)

    source = algorithm_source
    if "reluctant_entry" in source and "def reluctant_entry" not in source:
        if "from algorithm_helpers import reluctant_entry" not in source:
            source = "from algorithm_helpers import reluctant_entry\n" + source

    exec(compile(source, "<user_algorithm>", "exec"), namespace, namespace)
    return namespace
