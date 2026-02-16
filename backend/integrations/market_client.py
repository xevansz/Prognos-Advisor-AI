from core.logging import get_logger

logger = get_logger(__name__)


async def get_macro_state() -> str:
    """
    Fetch and classify macro market state.
    
    For MVP, returns a simple heuristic-based classification.
    Future: Integrate with real market data APIs.
    """
    return "sideways"
