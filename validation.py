"""Input validation for production simulation requests."""

from bi_suite import ALGORITHMS

ALLOWED_PERIODS = frozenset({"1d", "5d", "1mo", "3mo", "6mo", "1y", "ytd", "5y", "max"})
ALLOWED_INTERVALS = frozenset({"1h", "1d", "1wk", "1mo"})

MAX_INITIAL_BALANCE = 10_000_000.0
MIN_INITIAL_BALANCE = 100.0
MAX_LOT_SIZE_PCT = 100
MIN_LOT_SIZE_PCT = 1
MAX_COMMISSION_PCT = 10
MIN_COMMISSION_PCT = 0
MAX_INITIAL_STOCKS = 1_000_000


def validate_simulation_form(form):
    symbol = str(form.get("symbol", "")).strip()
    if not symbol:
        raise ValueError("Stock symbol is required.")

    period = str(form.get("period", "")).strip()
    if period not in ALLOWED_PERIODS:
        raise ValueError(f"Period '{period}' is not allowed.")

    interval = str(form.get("interval", "")).strip()
    if interval not in ALLOWED_INTERVALS:
        raise ValueError(f"Interval '{interval}' is not allowed.")

    algorithm = str(form.get("algorithm", "")).strip()
    if algorithm not in ALGORITHMS:
        raise ValueError("Select one of the available algorithms.")

    try:
        lot_size_pct = int(form.get("lot_size", 75))
        initial_balance = float(form.get("initial_balance", 10000))
        commission_pct = int(form.get("comission", 1))
        initial_stocks = int(form.get("initial_stocks", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid numeric parameter.") from exc

    if not MIN_INITIAL_BALANCE <= initial_balance <= MAX_INITIAL_BALANCE:
        raise ValueError(
            f"Initial balance must be between {MIN_INITIAL_BALANCE:,.0f} "
            f"and {MAX_INITIAL_BALANCE:,.0f}."
        )
    if not MIN_LOT_SIZE_PCT <= lot_size_pct <= MAX_LOT_SIZE_PCT:
        raise ValueError(f"Lot size must be between {MIN_LOT_SIZE_PCT}% and {MAX_LOT_SIZE_PCT}%.")
    if not MIN_COMMISSION_PCT <= commission_pct <= MAX_COMMISSION_PCT:
        raise ValueError(
            f"Commission must be between {MIN_COMMISSION_PCT}% and {MAX_COMMISSION_PCT}%."
        )
    if not 0 <= initial_stocks <= MAX_INITIAL_STOCKS:
        raise ValueError(f"Initial stocks must be between 0 and {MAX_INITIAL_STOCKS:,}.")

    return {
        "symbol": symbol,
        "period": period,
        "interval": interval,
        "algorithm": algorithm,
        "lot_size_pct": lot_size_pct,
        "initial_balance": initial_balance,
        "commission_pct": commission_pct,
        "initial_stocks": initial_stocks,
    }
