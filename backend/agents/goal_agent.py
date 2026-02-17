from datetime import datetime
from decimal import Decimal

from core.logging import get_logger

logger = get_logger(__name__)


def evaluate_goals(
    goals: list[dict],
    monthly_savings: float,
    base_currency: str,
) -> list[dict]:
    """
    Evaluate goal feasibility based on current savings rate.
    
    Args:
        goals: List of goal dicts with 'id', 'target_amount', 'target_date', 'priority'
        monthly_savings: Current monthly savings (credits - debits)
        base_currency: User's base currency
        
    Returns:
        List of dicts with goal_id, status, required_monthly_savings, actual_monthly_savings
    """
    
    results = []
    
    for goal in goals:
        goal_id = goal.get("id")
        target_amount = Decimal(str(goal.get("target_amount", 0)))
        target_date = goal.get("target_date")
        
        if not target_date:
            continue
        
        if isinstance(target_date, str):
            target_date = datetime.fromisoformat(target_date.replace("Z", "+00:00")).date()
        
        months_remaining = max(
            1,
            (target_date.year - datetime.utcnow().year) * 12
            + (target_date.month - datetime.utcnow().month),
        )
        
        required_monthly = float(target_amount / Decimal(str(months_remaining)))
        
        if monthly_savings >= required_monthly * 1.1:
            status = "on_track"
        elif monthly_savings >= required_monthly * 0.7:
            status = "at_risk"
        else:
            status = "unrealistic"
        
        results.append({
            "goal_id": goal_id,
            "status": status,
            "required_monthly_savings": required_monthly,
            "actual_monthly_savings": monthly_savings,
        })
    
    return results
