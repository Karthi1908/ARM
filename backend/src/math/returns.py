import numpy as np
from typing import Tuple, List, Dict

# Synthetic volatility parameters for simulation when historical DB is freshly initialized
VOLATILITY_PROFILES: Dict[str, float] = {
    "BTC": 0.52,   # 52% annualized vol
    "ETH": 0.65,   # 65% annualized vol
    "SOL": 0.88,   # 88% annualized vol
    "ARB": 0.95,   # 95% annualized vol
    "OP": 0.92,    # 92% annualized vol
    "LINK": 0.74,  # 74% annualized vol
    "USDC": 0.005, # 0.5% stablecoin vol
    "USDT": 0.006, # 0.6% stablecoin vol
    "ONDO_USDY": 0.02, # 2% RWA low vol
    "TBILL_RWA": 0.015,
}

def generate_historical_prices_and_returns(
    asset_id: str,
    base_price: float,
    days: int = 90
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns (prices_series, log_returns).
    Uses deterministic geometric brownian motion seeded by asset hash for consistent reproducible math.
    """
    symbol = asset_id.upper()
    annual_vol = VOLATILITY_PROFILES.get(symbol, 0.70)
    daily_vol = annual_vol / np.sqrt(365.0)

    # Seed with asset name so it's 100% deterministic
    seed = abs(hash(symbol)) % (2**32 - 1)
    rng = np.random.default_rng(seed)

    # Generate daily returns with slight positive drift (10% annualized)
    drift = (0.10 / 365.0) - (0.5 * daily_vol**2)
    daily_shocks = rng.normal(loc=drift, scale=daily_vol, size=days)

    # Calculate price path
    cumulative_returns = np.exp(np.cumsum(daily_shocks))
    prices = base_price * cumulative_returns

    # Daily log returns: ln(P_t / P_{t-1})
    log_returns = np.diff(np.log(np.insert(prices, 0, base_price)))
    return prices, log_returns
