import numpy as np
from typing import List, Dict, Any
from backend.src.math.greeks import compute_position_greeks
from backend.src.math.covariance import compute_portfolio_covariance_matrix
from backend.src.math.beta import calculate_beta
from backend.src.math.returns import generate_historical_prices_and_returns
from backend.src.services.oracles import oracle_service

async def compute_portfolio_risk_profile(
    positions_data: List[Dict[str, Any]],
    lookback_days: int = 90,
    risk_free_rate: float = 0.00
) -> Dict[str, Any]:
    """
    Aggregates whole-portfolio Net Delta, Net Vega, Net Gamma,
    computes NxN covariance matrix, and calculates portfolio-wide Sharpe & Treynor ratios.
    """
    # Filter out unpriced or zero-value positions from risk weighting and covariance matrix
    priced_positions = [
        p for p in positions_data
        if float(p.get("total_value_usd") or 0.0) > 0.0 and float(p.get("unit_price_usd") or 0.0) > 0.0
    ]

    if not priced_positions:
        return {
            "net_delta": 0.0,
            "net_gamma": 0.0,
            "net_vega": 0.0,
            "sharpe_ratio": 0.0,
            "treynor_ratio": 0.0,
            "assets": [],
            "covariance_matrix": [],
            "correlation_matrix": [],
            "portfolio_volatility": 0.0,
            "portfolio_return": 0.0
        }

    total_portfolio_value = sum([float(p["total_value_usd"]) for p in priced_positions])
    if total_portfolio_value <= 0:
        total_portfolio_value = 1.0

    net_delta = 0.0
    net_gamma = 0.0
    net_vega = 0.0

    symbols = []
    weights = []
    betas = []
    annual_returns = []

    # Benchmark BTC return series
    btc_price, _, _ = await oracle_service.get_price("BTC")
    _, btc_ret = generate_historical_prices_and_returns("BTC", btc_price, days=lookback_days)

    for p in priced_positions:
        sym = p["symbol"].upper()
        symbols.append(sym)
        weight = float(p["total_value_usd"]) / total_portfolio_value
        weights.append(weight)

        # Greeks
        g = compute_position_greeks(
            spot_price=float(p["unit_price_usd"]),
            quantity=float(p["quantity"]),
            asset_class=p.get("asset_class", "crypto"),
            trade_type=p.get("trade_type", "spot")
        )
        net_delta += g["delta"]
        net_gamma += g["gamma"]
        net_vega += g["vega"]

        # Asset return and beta
        price, _, _ = await oracle_service.get_price(sym)
        _, ret = generate_historical_prices_and_returns(sym, price, days=lookback_days)
        b = calculate_beta(ret, btc_ret) if sym != "BTC" else 1.0
        betas.append(b)
        annual_returns.append(float(np.mean(ret)) * 365.0)

    # Covariance Matrix
    unique_symbols, cov_matrix, corr_matrix = await compute_portfolio_covariance_matrix(symbols, lookback_days)

    # Portfolio Variance = w^T * Sigma * w
    w_vec = np.array(weights)
    cov_arr = np.array(cov_matrix)
    
    # Check dimensions matching
    if cov_arr.shape == (len(w_vec), len(w_vec)):
        port_var = float(np.dot(w_vec.T, np.dot(cov_arr, w_vec)))
    else:
        port_var = 0.25  # Fallback 50% annual vol
    
    port_vol = max(np.sqrt(max(port_var, 1e-6)), 0.01)
    port_return = float(np.dot(w_vec, np.array(annual_returns)))
    port_beta = float(np.dot(w_vec, np.array(betas)))

    # Sharpe & Treynor (Rf = 0)
    port_sharpe = float((port_return - risk_free_rate) / port_vol)
    port_treynor = float((port_return - risk_free_rate) / port_beta) if abs(port_beta) > 1e-4 else 0.0

    return {
        "net_delta": round(net_delta, 4),
        "net_gamma": round(net_gamma, 6),
        "net_vega": round(net_vega, 4),
        "sharpe_ratio": round(port_sharpe, 4),
        "treynor_ratio": round(port_treynor, 4),
        "assets": unique_symbols,
        "covariance_matrix": cov_matrix,
        "correlation_matrix": corr_matrix,
        "portfolio_volatility": round(port_vol, 4),
        "portfolio_return": round(port_return, 4)
    }
