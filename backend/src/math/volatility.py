import numpy as np
from typing import Tuple

def calculate_volatility_and_std(
    returns: np.ndarray,
    annualization_factor: float = 365.0
) -> Tuple[float, float]:
    """
    Computes (annualized_volatility, daily_standard_deviation) of returns series.
    """
    if len(returns) < 2:
        return 0.0, 0.0

    daily_std = float(np.std(returns, ddof=1))
    annualized_vol = float(daily_std * np.sqrt(annualization_factor))

    return round(annualized_vol, 4), round(daily_std, 6)

def calculate_delta(
    side: str = "buy",
    trade_type: str = "spot",
    strike: float | None = None,
    spot: float | None = None
) -> float:
    """Computes directional Delta sensitivity."""
    multiplier = 1.0 if side.lower() == "buy" else -1.0

    if trade_type in ["spot", "forward", "future"]:
        return multiplier * 1.0
    elif trade_type == "option_call":
        return multiplier * 0.55  # Representative ATM call delta
    elif trade_type == "option_put":
        return multiplier * (-0.45)  # Representative ATM put delta

    return multiplier * 1.0
