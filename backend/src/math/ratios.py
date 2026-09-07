import numpy as np
from typing import Tuple

def calculate_sharpe_and_treynor(
    returns: np.ndarray,
    beta: float,
    risk_free_rate: float = 0.00,
    annualization_factor: float = 365.0
) -> Tuple[float, float]:
    """
    Computes (Sharpe Ratio, Treynor Ratio) assuming risk_free_rate = 0.00:
    Sharpe = (E[R] - Rf) / sigma * sqrt(365)
    Treynor = (E[R_annual] - Rf) / Beta
    """
    if len(returns) < 2:
        return 0.0, 0.0

    mean_daily_return = float(np.mean(returns))
    daily_std = float(np.std(returns, ddof=1))
    annual_return = mean_daily_return * annualization_factor

    # Sharpe Ratio
    if daily_std < 1e-8:
        sharpe = 0.0
    else:
        sharpe = float(((mean_daily_return - (risk_free_rate / annualization_factor)) / daily_std) * np.sqrt(annualization_factor))

    # Treynor Ratio
    if abs(beta) < 1e-6:
        treynor = 0.0
    else:
        treynor = float((annual_return - risk_free_rate) / beta)

    return round(sharpe, 4), round(treynor, 4)
