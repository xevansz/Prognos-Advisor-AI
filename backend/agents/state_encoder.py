from typing import List

"""
We are a building a state vector for RL.
The model expects these values (risk, goals, equity, runway)

All values:
* same length(5)
* same range([0,1])
* same order

If the order changes, RL will get confused.
"""


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    """
    Ensures the numbers are in the range of [min_value, max_value]
    """
    return max(min_value, min(value, max_value))


def encode_state(
    risk_metrics: dict,
    goal_evaluations: List[dict],
    allocation: dict,
    monthly_savings_rate: float,
) -> List[float]:
    """
    Convert the raw outputs to a normalized fixed length state vector

    Returns:
      List[float] of length 5, all values in [0,1]
    """
    # risk
    risk_score = risk_metrics.get("risk_score", 50)
    normalize_risk = clamp(risk_score / 100)

    # goal
    if goal_evaluations:
        probabilities = [
            goal.get("success_probability", 0.5) for goal in goal_evaluations
        ]
        goal_feasibility = sum(probabilities) / len(probabilities)
    else:
        goal_feasibility = 0.5

    goal_feasibility = clamp(goal_feasibility)

    # equity
    equity_ratio = allocation.get("recommended", {}).get("equity", 0.5)
    equity_ratio = clamp(equity_ratio)

    # monthly savings rate
    normalized_savings = clamp(monthly_savings_rate)

    # runway months
    runway_months = risk_metrics.get("runway_months", 0)
    normalized_runway = clamp(min(runway_months / 12, 1.0))

    return [
        normalize_risk,
        goal_feasibility,
        equity_ratio,
        normalized_savings,
        normalized_runway,
    ]
