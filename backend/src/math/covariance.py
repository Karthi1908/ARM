import numpy as np
from typing import List, Dict, Tuple, Any
from backend.src.core.redis_client import redis_manager
from backend.src.math.returns import generate_historical_prices_and_returns
from backend.src.services.oracles import oracle_service

async def compute_portfolio_covariance_matrix(
    asset_symbols: List[str],
    lookback_days: int = 90
) -> Tuple[List[str], List[List[float]], List[List[float]]]:
    """
    Computes (unique_assets, covariance_matrix, correlation_matrix).
    Caches in Redis with 120s TTL.
    """
    unique_assets = sorted(list(set([a.upper() for a in asset_symbols])))
    if not unique_assets:
        return [], [], []

    cache_key = f"cov_matrix:{'_'.join(unique_assets)}:{lookback_days}"
    cached = await redis_manager.get(cache_key)
    if cached:
        return cached["assets"], cached["covariance"], cached["correlation"]

    # Generate aligned return series for each asset
    returns_matrix = []
    for sym in unique_assets:
        price, _, _ = await oracle_service.get_price(sym)
        _, ret = generate_historical_prices_and_returns(sym, price, days=lookback_days)
        returns_matrix.append(ret)

    # Convert to 2D numpy array (assets x days)
    data = np.array(returns_matrix)

    # Annualized covariance matrix: cov(daily) * 365
    cov_daily = np.cov(data, ddof=1)
    if cov_daily.ndim == 0:  # Single asset case
        cov_annual = np.array([[float(cov_daily) * 365.0]])
        corr_matrix = np.array([[1.0]])
    else:
        cov_annual = cov_daily * 365.0
        # Correlation matrix
        std_devs = np.sqrt(np.diag(cov_daily))
        outer_std = np.outer(std_devs, std_devs)
        corr_matrix = np.divide(cov_daily, outer_std, out=np.zeros_like(cov_daily), where=outer_std!=0)
        np.fill_diagonal(corr_matrix, 1.0)

    cov_list = [[round(float(val), 6) for val in row] for row in cov_annual]
    corr_list = [[round(float(val), 4) for val in row] for row in corr_matrix]

    await redis_manager.set(
        cache_key,
        {"assets": unique_assets, "covariance": cov_list, "correlation": corr_list},
        ttl_seconds=120
    )

    return unique_assets, cov_list, corr_list
