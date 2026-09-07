import numpy as np
from scipy.stats import norm
from typing import Tuple, Dict, Any

def compute_position_greeks(
    spot_price: float,
    quantity: float,
    asset_class: str = "crypto",
    trade_type: str = "spot",
    strike: float | None = None,
    expiry_years: float = 0.25,
    volatility: float = 0.65,
    risk_free_rate: float = 0.00
) -> Dict[str, float]:
    """
    Computes position-weighted Greeks: Delta (USD/point), Gamma (Delta change/point), Vega (USD/1% vol).
    """
    qty = float(quantity)
    if qty == 0:
        return {"delta": 0.0, "gamma": 0.0, "vega": 0.0}

    # Linear Spot, Forward, or Perpetual Contracts (unless option contract)
    if trade_type not in ["option_call", "option_put"]:
        return {
            "delta": round(qty, 4),
            "gamma": 0.0000,
            "vega": 0.0000
        }

    # Non-linear Options Contracts
    S = max(spot_price, 1e-6)
    K = strike if strike and strike > 0 else S
    T = max(expiry_years, 1.0 / 365.0)
    sigma = max(volatility, 0.01)
    r = risk_free_rate

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    pdf_d1 = norm.pdf(d1)

    if trade_type == "option_call":
        unit_delta = norm.cdf(d1)
    elif trade_type == "option_put":
        unit_delta = norm.cdf(d1) - 1.0
    else:
        unit_delta = 1.0

    unit_gamma = pdf_d1 / (S * sigma * np.sqrt(T))
    unit_vega = (S * np.sqrt(T) * pdf_d1) / 100.0  # Sensitivity to 1% shift in vol

    return {
        "delta": round(qty * unit_delta, 4),
        "gamma": round(qty * unit_gamma, 6),
        "vega": round(qty * unit_vega, 4)
    }
