import pytest
from backend.src.services.uniswap_ai import uniswap_ai_service

def test_parse_hedge_intent_missing_parameters():
    # User just says "hedge" with no token or quantity
    intent = uniswap_ai_service.parse_hedge_intent("I want to hedge my position")
    assert not intent["is_complete"]
    assert "token" in intent["missing_parameters"]
    assert "quantity" in intent["missing_parameters"]
    assert "Which token and what quantity" in intent["prompt_text"]

def test_parse_hedge_intent_missing_quantity():
    intent = uniswap_ai_service.parse_hedge_intent("Convert my ETH to USDC")
    assert not intent["is_complete"]
    assert intent["source_token"] == "ETH"
    assert intent["target_token"] == "USDC"
    assert "quantity" in intent["missing_parameters"]
    assert "How much ETH" in intent["prompt_text"]

def test_parse_hedge_intent_complete_explicit():
    intent = uniswap_ai_service.parse_hedge_intent("Convert 2.5 ETH into USDC")
    assert intent["is_complete"]
    assert intent["source_token"] == "ETH"
    assert intent["target_token"] == "USDC"
    assert intent["quantity"] == "2.5"
    assert intent["missing_parameters"] == []

def test_parse_hedge_intent_percentage_with_positions():
    positions = [
        {"symbol": "ETH", "quantity": 4.0, "total_value_usd": 14200.0},
        {"symbol": "SOL", "quantity": 20.0, "total_value_usd": 2900.0}
    ]
    intent = uniswap_ai_service.parse_hedge_intent("Convert 50% of my ETH to USDC", positions)
    assert intent["is_complete"]
    assert intent["source_token"] == "ETH"
    assert intent["target_token"] == "USDC"
    assert float(intent["quantity"]) == 2.0

def test_parse_hedge_intent_target_eth():
    intent = uniswap_ai_service.parse_hedge_intent("Convert 500 USDC to ETH")
    assert intent["is_complete"]
    assert intent["source_token"] == "USDC"
    assert intent["target_token"] == "ETH"
    assert intent["quantity"] == "500"

@pytest.mark.asyncio
async def test_get_hedge_quote_uniswap_route():
    quote = await uniswap_ai_service.get_hedge_quote(
        chain_id=1,
        from_token="ETH",
        to_token="USDC",
        amount="2.0"
    )
    assert quote["venue"] == "uniswap"
    assert quote["from_token"] == "ETH"
    assert quote["to_token"] == "USDC"
    assert float(quote["from_amount"]) == 2.0
    assert float(quote["to_amount"]) > 0
    assert "route_summary" in quote
    assert "Uniswap" in quote["route_summary"]
    assert quote["requires_user_signature"] is True
    assert "unsigned_tx" in quote
    assert quote["unsigned_tx"]["to"].startswith("0x")
