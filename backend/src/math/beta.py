import numpy as np

def calculate_beta(
    asset_returns: np.ndarray,
    benchmark_returns: np.ndarray
) -> float:
    """
    Computes Beta of an asset relative to Bitcoin benchmark returns:
    Beta = Cov(R_asset, R_btc) / Var(R_btc)
    """
    if len(asset_returns) != len(benchmark_returns):
        min_len = min(len(asset_returns), len(benchmark_returns))
        asset_returns = asset_returns[-min_len:]
        benchmark_returns = benchmark_returns[-min_len:]

    var_benchmark = np.var(benchmark_returns, ddof=1)
    if var_benchmark < 1e-12:
        return 1.0

    covariance_matrix = np.cov(asset_returns, benchmark_returns, ddof=1)
    covariance = covariance_matrix[0, 1]

    beta = float(covariance / var_benchmark)
    return round(beta, 4)
