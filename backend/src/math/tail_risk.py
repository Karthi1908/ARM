import numpy as np
from scipy.stats import norm
from typing import Dict, Any, List

def calculate_tail_risk(
    portfolio_value_usd: float,
    portfolio_daily_return: float,
    portfolio_daily_vol: float,
    historical_simulated_returns: np.ndarray | None = None
) -> Dict[str, float]:
    """
    Computes 1-day Value at Risk (VaR) and Expected Shortfall (CVaR/ES)
    at 95% and 99% confidence horizons in USD.
    """
    if portfolio_value_usd <= 0.0:
        return {
            "var_95_usd": 0.0,
            "var_99_usd": 0.0,
            "es_95_usd": 0.0,
            "es_99_usd": 0.0
        }

    port_val = portfolio_value_usd
    mu = portfolio_daily_return
    sigma = max(portfolio_daily_vol, 0.001)

    # 1. Parametric VaR
    # z_0.95 = 1.6449, z_0.99 = 2.3263
    z_95 = norm.ppf(0.95)
    z_99 = norm.ppf(0.99)

    var_95_pct = z_95 * sigma - mu
    var_99_pct = z_99 * sigma - mu

    var_95_usd = max(var_95_pct * port_val, 0.0)
    var_99_usd = max(var_99_pct * port_val, 0.0)

    # 2. Expected Shortfall (Conditional VaR)
    # Under normality: ES_alpha = mu + sigma * (pdf(z_alpha) / (1 - alpha))
    es_95_pct = (sigma * norm.pdf(z_95) / 0.05) - mu
    es_99_pct = (sigma * norm.pdf(z_99) / 0.01) - mu

    es_95_usd = max(es_95_pct * port_val, var_95_usd * 1.15)
    es_99_usd = max(es_99_pct * port_val, var_99_usd * 1.20)

    # If historical simulated returns provided, blend with empirical quantiles
    if historical_simulated_returns is not None and len(historical_simulated_returns) >= 20:
        hist_var_95_pct = -float(np.percentile(historical_simulated_returns, 5.0))
        hist_var_99_pct = -float(np.percentile(historical_simulated_returns, 1.0))

        # Tail losses beyond 95%
        tail_95 = historical_simulated_returns[historical_simulated_returns <= -hist_var_95_pct]
        tail_99 = historical_simulated_returns[historical_simulated_returns <= -hist_var_99_pct]

        hist_es_95_pct = -float(np.mean(tail_95)) if len(tail_95) > 0 else hist_var_95_pct * 1.2
        hist_es_99_pct = -float(np.mean(tail_99)) if len(tail_99) > 0 else hist_var_99_pct * 1.25

        # Average parametric and historical
        var_95_usd = round(float(0.5 * var_95_usd + 0.5 * max(hist_var_95_pct * port_val, 0.0)), 2)
        var_99_usd = round(float(0.5 * var_99_usd + 0.5 * max(hist_var_99_pct * port_val, 0.0)), 2)
        es_95_usd = round(float(0.5 * es_95_usd + 0.5 * max(hist_es_95_pct * port_val, 0.0)), 2)
        es_99_usd = round(float(0.5 * es_99_usd + 0.5 * max(hist_es_99_pct * port_val, 0.0)), 2)
    else:
        var_95_usd = round(float(var_95_usd), 2)
        var_99_usd = round(float(var_99_usd), 2)
        es_95_usd = round(float(es_95_usd), 2)
        es_99_usd = round(float(es_99_usd), 2)

    return {
        "var_95_usd": var_95_usd,
        "var_99_usd": var_99_usd,
        "es_95_usd": es_95_usd,
        "es_99_usd": es_99_usd
    }
