import random
from datetime import datetime
from decimal import Decimal

from core.logging import get_logger

logger = get_logger(__name__)


def evaluate_goals(
    goals: list[dict],
    monthly_savings: float,
    base_currency: str,
    current_savings: float = 0.0,
    expected_return: float = 0.07,
) -> list[dict]:
    """
    Evaluate goal feasibility using Monte Carlo simulation and Future Value calculation.

    Args:
        goals: List of goal dicts with 'id', 'target_amount', 'target_date', 'priority'
        monthly_savings: Current monthly savings (credits - debits)
        base_currency: User's base currency
        current_savings: Current amount saved towards goals
        expected_return: Expected annual return rate (default 7%)

    Returns:
        List of dicts with goal_id, status, projected_value, success_probability, goal_pressure
    """

    results = []

    for goal in goals:
        goal_id = goal.get("id")
        target_amount = Decimal(str(goal.get("target_amount", 0)))
        target_date = goal.get("target_date")

        if not target_date:
            continue

        if isinstance(target_date, str):
            target_date = datetime.fromisoformat(
                target_date.replace("Z", "+00:00")
            ).date()

        months_remaining = max(
            1,
            (target_date.year - datetime.utcnow().year) * 12
            + (target_date.month - datetime.utcnow().month),
        )

        # Calculate Future Value using compound interest formula
        # FV = current_savings*(1+r)^t + contribution * ((1+r)^t - 1)/r
        monthly_rate = expected_return / 12.0

        if monthly_rate > 0:
            future_value_savings = float(
                Decimal(str(current_savings))
                * Decimal(str((1 + monthly_rate) ** months_remaining))
            )
            future_value_contributions = float(
                Decimal(str(monthly_savings))
                * Decimal(
                    str(((1 + monthly_rate) ** months_remaining - 1) / monthly_rate)
                )
            )
            projected_value = future_value_savings + future_value_contributions
        else:
            projected_value = current_savings + (monthly_savings * months_remaining)

        # Monte Carlo simulation with 500 runs
        num_simulations = 500
        successful_runs = 0

        for _ in range(num_simulations):
            # Simulate with random returns (normal distribution around expected return)
            # Standard deviation of ~15% for stock market volatility
            simulated_return = random.gauss(expected_return, 0.15)
            simulated_monthly_rate = simulated_return / 12.0

            if simulated_monthly_rate > -0.05:  # Avoid extreme negative scenarios
                sim_fv_savings = current_savings * (
                    (1 + simulated_monthly_rate) ** months_remaining
                )
                if simulated_monthly_rate != 0:
                    sim_fv_contributions = monthly_savings * (
                        ((1 + simulated_monthly_rate) ** months_remaining - 1)
                        / simulated_monthly_rate
                    )
                else:
                    sim_fv_contributions = monthly_savings * months_remaining

                sim_total = sim_fv_savings + sim_fv_contributions

                if sim_total >= float(target_amount):
                    successful_runs += 1

        success_probability = successful_runs / num_simulations
        goal_pressure = 1.0 - success_probability

        # Determine status based on success probability
        if success_probability >= 0.75:
            status = "on_track"
        elif success_probability >= 0.40:
            status = "at_risk"
        else:
            status = "unrealistic"

        results.append(
            {
                "goal_id": goal_id,
                "goal_name": goal.get("name", "Unknown"),
                "status": status,
                "projected_value": round(projected_value, 2),
                "success_probability": round(success_probability, 2),
                "goal_pressure": round(goal_pressure, 2),
                "required_monthly_savings": round(
                    float(target_amount) / months_remaining, 2
                ),
                "actual_monthly_savings": monthly_savings,
            }
        )

    return results
