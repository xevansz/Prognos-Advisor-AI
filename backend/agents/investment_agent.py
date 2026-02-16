from core.logging import get_logger

logger = get_logger(__name__)


def recommend_allocation(
    risk_capacity_score: int,
    risk_appetite: str,
    goals_summary: list[dict],
    macro_state: str,
) -> dict:
    """
    Recommend asset allocation based on risk profile and goals.
    
    Args:
        risk_capacity_score: Risk capacity (0-100)
        risk_appetite: 'conservative', 'moderate', or 'aggressive'
        goals_summary: List of goal evaluation results
        macro_state: Current macro market state
        
    Returns:
        Dict with 'recommended' allocation and optional 'aggressive_alternative'
    """
    
    appetite_map = {
        "conservative": 0.3,
        "moderate": 0.5,
        "aggressive": 0.7,
    }
    
    appetite_factor = appetite_map.get(risk_appetite, 0.5)
    capacity_factor = risk_capacity_score / 100.0
    
    effective_risk = min(appetite_factor, capacity_factor)
    
    if effective_risk >= 0.6:
        recommended = {
            "cash": 0.10,
            "debt": 0.30,
            "equity": 0.55,
            "other": 0.05,
        }
    elif effective_risk >= 0.4:
        recommended = {
            "cash": 0.15,
            "debt": 0.40,
            "equity": 0.40,
            "other": 0.05,
        }
    else:
        recommended = {
            "cash": 0.25,
            "debt": 0.50,
            "equity": 0.20,
            "other": 0.05,
        }
    
    aggressive_alternative = None
    if risk_appetite == "aggressive" and capacity_factor < 0.5:
        aggressive_alternative = {
            "cash": 0.05,
            "debt": 0.20,
            "equity": 0.70,
            "other": 0.05,
        }
    
    return {
        "recommended": recommended,
        "aggressive_alternative": aggressive_alternative,
    }
