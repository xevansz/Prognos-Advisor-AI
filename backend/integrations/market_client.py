from core.logging import get_logger

logger = get_logger(__name__)


async def fetch_market_indicators() -> dict:
    """
    Fetch market indicators from external API.

    For MVP, returns mock data. In production, integrate with:
    - Yahoo Finance API
    - Alpha Vantage
    - Federal Reserve Economic Data (FRED)
    """
    # Mock data for MVP - replace with real API calls
    return {
        "index_level": 4500.0,
        "index_200d_ma": 4400.0,
        "short_rate": 0.045,  # 4.5%
        "inflation_rate": 0.032,  # 3.2%
        "vix_level": 18.5,  # Volatility index
    }


async def get_macro_state() -> str:
    """
    Classify macro market state based on indicators.

    Returns one of: 'bull', 'bear', 'recession', 'sideways'

    Classification logic:
    - Bull: index > 200d MA, low volatility, positive momentum
    - Bear: index < 200d MA, high volatility, negative momentum
    - Recession: high unemployment indicators, inverted yield curve signals
    - Sideways: neutral conditions
    """
    try:
        indicators = await fetch_market_indicators()

        index_level = indicators.get("index_level", 0)
        index_200d_ma = indicators.get("index_200d_ma", 0)
        short_rate = indicators.get("short_rate", 0)
        inflation_rate = indicators.get("inflation_rate", 0)
        vix_level = indicators.get("vix_level", 20)

        # Calculate key metrics
        trend_strength = (
            (index_level - index_200d_ma) / index_200d_ma if index_200d_ma > 0 else 0
        )
        is_above_ma = index_level > index_200d_ma
        high_volatility = vix_level > 25

        # Recession signals
        high_rates = short_rate > 0.05
        high_inflation = inflation_rate > 0.04

        # Classification logic
        if high_rates and high_inflation and not is_above_ma:
            return "recession"
        elif is_above_ma and trend_strength > 0.05 and not high_volatility:
            return "bull"
        elif not is_above_ma and (high_volatility or trend_strength < -0.10):
            return "bear"
        else:
            return "sideways"

    except Exception as e:
        logger.error(f"Failed to fetch market indicators: {e}")
        return "sideways"  # Safe default
