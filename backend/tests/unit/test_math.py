import pytest
import numpy as np
from backend.src.math.beta import calculate_beta
from backend.src.math.volatility import calculate_volatility_and_std, calculate_delta
from backend.src.math.ratios import calculate_sharpe_and_treynor
from backend.src.math.greeks import compute_position_greeks
from backend.src.math.tail_risk import calculate_tail_risk

def test_beta_calculation():
    # Asset identical to benchmark should have Beta = 1.0
    btc_returns = np.array([0.01, -0.02, 0.03, 0.015, -0.01])
    beta_self = calculate_beta(btc_returns, btc_returns)
    assert abs(beta_self - 1.0) < 1e-4

    # Amplified asset (2x returns) should have Beta = 2.0
    amplified_returns = btc_returns * 2.0
    beta_2x = calculate_beta(amplified_returns, btc_returns)
    assert abs(beta_2x - 2.0) < 1e-4

def test_volatility_and_delta():
    returns = np.array([0.01, -0.01, 0.02, -0.02, 0.015])
    ann_vol, daily_std = calculate_volatility_and_std(returns)
    assert ann_vol > 0
    assert daily_std > 0

    # Spot buy delta
    delta_buy = calculate_delta(side="buy", trade_type="spot")
    assert delta_buy == 1.0

    # Spot sell delta
    delta_sell = calculate_delta(side="sell", trade_type="spot")
    assert delta_sell == -1.0

def test_sharpe_and_treynor_rf_zero():
    # Mean return 0.001 daily (~36.5% annual), std 0.01 daily
    returns = np.array([0.005, 0.001, -0.002, 0.003, -0.001, 0.004])
    beta = 1.2
    sharpe, treynor = calculate_sharpe_and_treynor(returns, beta, risk_free_rate=0.0)
    assert sharpe > 0
    assert treynor > 0

def test_greeks_computation():
    # Spot position has Delta = qty, Gamma = 0, Vega = 0
    spot_greeks = compute_position_greeks(spot_price=3500.0, quantity=2.5, trade_type="spot")
    assert spot_greeks["delta"] == 2.5
    assert spot_greeks["gamma"] == 0.0
    assert spot_greeks["vega"] == 0.0

    # Option call has positive Gamma and Vega
    call_greeks = compute_position_greeks(
        spot_price=3500.0,
        quantity=1.0,
        trade_type="option_call",
        strike=3500.0,
        expiry_years=0.25,
        volatility=0.60
    )
    assert 0.4 < call_greeks["delta"] < 0.7
    assert call_greeks["gamma"] > 0
    assert call_greeks["vega"] > 0

def test_tail_risk_monotonicity():
    # At 99% confidence, VaR and ES must be greater than at 95%
    tail = calculate_tail_risk(
        portfolio_value_usd=100000.0,
        portfolio_daily_return=0.001,
        portfolio_daily_vol=0.03
    )
    assert tail["var_99_usd"] > tail["var_95_usd"]
    assert tail["es_95_usd"] >= tail["var_95_usd"]
    assert tail["es_99_usd"] >= tail["var_99_usd"]

def test_math_engine_version_tagging():
    from backend.src.core.config import settings
    from backend.src.models.schemas import SingleRiskResponse, PortfolioRiskResponse, RiskReportResponse
    from datetime import datetime

    assert settings.MATH_ENGINE_VERSION == "v1.1.0"
    
    single = SingleRiskResponse(
        asset_id="ETH",
        beta=1.1,
        delta=1.0,
        volatility_annualized=0.65,
        standard_deviation=0.03,
        sharpe_ratio=1.5,
        treynor_ratio=1.2,
        historical_points_used=90,
        math_engine_version=settings.MATH_ENGINE_VERSION
    )
    assert single.math_engine_version == "v1.1.0"

    port = PortfolioRiskResponse(
        wallet_address="0x123",
        net_delta=10.0,
        net_gamma=0.0,
        net_vega=0.0,
        sharpe_ratio=1.4,
        treynor_ratio=1.1,
        assets=["ETH"],
        covariance_matrix=[[0.05]],
        correlation_matrix=[[1.0]],
        math_engine_version=settings.MATH_ENGINE_VERSION
    )
    assert port.math_engine_version == "v1.1.0"

