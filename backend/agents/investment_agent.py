from core.logging import get_logger

logger = get_logger(__name__)


def recommend_allocation(
    risk_capacity_score: int,
    risk_appetite: str,
    goals_summary: list[dict],
    macro_state: str,
    age: int = 35,
    goal_time_horizon: int = 10,
) -> dict:
    """
    Recommend asset allocation based on risk profile, age, goals, and market conditions.
    
    Args:
        risk_capacity_score: Risk capacity (0-100)
        risk_appetite: 'conservative', 'moderate', or 'aggressive'
        goals_summary: List of goal evaluation results
        macro_state: Current macro market state ('bull', 'bear', 'recession', 'sideways')
        age: User's age (used for baseline equity allocation)
        goal_time_horizon: Years until primary goal (affects risk tolerance)
        
    Returns:
        Dict with 'recommended' allocation and optional 'aggressive_alternative'
    """
    
    # Step 1: Calculate baseline equity allocation using age rule
    # Equity_ratio = 100 - age (clamped to reasonable bounds)
    baseline_equity = max(20, min(80, 100 - age))
    
    # Step 2: Adjust for time horizon (longer horizon = more equity)
    if goal_time_horizon > 15:
        horizon_adjustment = 10
    elif goal_time_horizon > 10:
        horizon_adjustment = 5
    elif goal_time_horizon < 3:
        horizon_adjustment = -10
    else:
        horizon_adjustment = 0
    
    # Step 3: Calculate goal pressure (average from goals)
    total_pressure = 0.0
    if goals_summary:
        for goal in goals_summary:
            total_pressure += goal.get("goal_pressure", 0.0)
        avg_goal_pressure = total_pressure / len(goals_summary)
    else:
        avg_goal_pressure = 0.0
    
    # High goal pressure = more conservative (reduce equity)
    pressure_adjustment = -int(avg_goal_pressure * 15)
    
    # Step 4: Apply risk appetite modifier
    appetite_map = {
        "conservative": -10,
        "moderate": 0,
        "aggressive": 10,
    }
    appetite_adjustment = appetite_map.get(risk_appetite, 0)
    
    # Step 5: Apply risk capacity constraint
    capacity_factor = risk_capacity_score / 100.0
    if capacity_factor < 0.3:
        capacity_adjustment = -15
    elif capacity_factor < 0.5:
        capacity_adjustment = -5
    else:
        capacity_adjustment = 0
    
    # Step 6: Adjust for macro state
    macro_adjustments = {
        "bull": 5,
        "sideways": 0,
        "bear": -10,
        "recession": -15,
    }
    macro_adjustment = macro_adjustments.get(macro_state, 0)
    
    # Calculate final equity percentage
    equity_pct = baseline_equity + horizon_adjustment + pressure_adjustment + \
                 appetite_adjustment + capacity_adjustment + macro_adjustment
    equity_pct = max(10, min(80, equity_pct))  # Clamp to [10, 80]
    
    # Allocate remaining to debt and cash
    remaining = 100 - equity_pct
    
    # Cash allocation based on risk capacity (higher risk = less cash needed)
    if capacity_factor >= 0.7:
        cash_pct = 5
    elif capacity_factor >= 0.5:
        cash_pct = 10
    else:
        cash_pct = 15
    
    debt_pct = remaining - cash_pct - 5  # Reserve 5% for other
    debt_pct = max(5, debt_pct)  # Ensure minimum debt allocation
    
    # Normalize to ensure sum = 100%
    total = equity_pct + debt_pct + cash_pct + 5
    
    recommended = {
        "equity": round(equity_pct / total, 3),
        "debt": round(debt_pct / total, 3),
        "cash": round(cash_pct / total, 3),
        "other": round(5 / total, 3),
    }
    
    # Create aggressive alternative if appetite and capacity mismatch
    aggressive_alternative = None
    if risk_appetite == "aggressive" and capacity_factor < 0.5:
        # More aggressive allocation despite low capacity (with warning)
        agg_equity = min(75, equity_pct + 15)
        agg_cash = 5
        agg_debt = 95 - agg_equity - agg_cash - 5
        
        aggressive_alternative = {
            "equity": round(agg_equity / 100, 3),
            "debt": round(agg_debt / 100, 3),
            "cash": round(agg_cash / 100, 3),
            "other": 0.05,
        }
    
    return {
        "recommended": recommended,
        "aggressive_alternative": aggressive_alternative,
    }
