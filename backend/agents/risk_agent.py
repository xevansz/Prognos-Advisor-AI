from datetime import datetime, timedelta
from decimal import Decimal

from core.logging import get_logger

logger = get_logger(__name__)


def compute_risk_metrics(
    transactions: list[dict],
    liquid_accounts: list[dict],
    base_currency: str,
    monthly_income: float = 0.0,
) -> dict:
    """
    Compute risk metrics: burn rate, runway, stability ratio, savings ratio, and risk score.

    Args:
        transactions: List of transaction dicts with 'amount', 'type', 'date'
        liquid_accounts: List of account dicts with 'balance' (in base currency)
        base_currency: User's base currency
        monthly_income: User's average monthly income

    Returns:
        Dict with burn_rate, runway_months, stability_ratio, savings_ratio, risk_score, risk_label
    """

    if not transactions:
        total_liquid = sum(
            Decimal(str(acc.get("balance", 0))) for acc in liquid_accounts
        )
        stability_ratio = 2.0 if monthly_income > 0 else 1.0
        savings_ratio = 1.0 if monthly_income > 0 else 0.0
        return {
            "burn_rate": 0.0,
            "runway_months": float("inf") if total_liquid > 0 else 0.0,
            "stability_ratio": stability_ratio,
            "savings_ratio": savings_ratio,
            "risk_score": 70,
            "risk_label": "Low",
        }

    cutoff_date = datetime.utcnow().date() - timedelta(days=60)
    recent_transactions = [
        tx for tx in transactions if tx.get("date") and tx["date"] >= cutoff_date
    ]

    total_debits = Decimal("0")
    total_credits = Decimal("0")

    for tx in recent_transactions:
        amount = Decimal(str(tx.get("amount", 0)))
        if tx.get("type") == "debit":
            total_debits += amount
        elif tx.get("type") == "credit":
            total_credits += amount

    days_in_period = min(60, (datetime.utcnow().date() - cutoff_date).days)
    if days_in_period == 0:
        days_in_period = 30

    monthly_debits = (total_debits / Decimal(str(days_in_period))) * Decimal("30")
    burn_rate = float(monthly_debits)

    total_liquid = sum(Decimal(str(acc.get("balance", 0))) for acc in liquid_accounts)

    if burn_rate > 0:
        runway_months = float(total_liquid / Decimal(str(burn_rate)))
    else:
        runway_months = float("inf") if total_liquid > 0 else 0.0

    # Calculate stability ratio: income / expenses
    if burn_rate > 0:
        stability_ratio = float(Decimal(str(monthly_income)) / Decimal(str(burn_rate)))
    else:
        stability_ratio = 2.0 if monthly_income > 0 else 1.0

    # Calculate savings ratio: (income - expenses) / income
    if monthly_income > 0:
        savings_ratio = float(
            (Decimal(str(monthly_income)) - Decimal(str(burn_rate)))
            / Decimal(str(monthly_income))
        )
        savings_ratio = max(0.0, min(1.0, savings_ratio))  # Clamp to [0, 1]
    else:
        savings_ratio = 0.0

    # Normalize function: clamp((x - min) / (max - min), 0, 1)
    def normalize(value: float, min_val: float, max_val: float) -> float:
        if max_val == min_val:
            return 0.5
        normalized = (value - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))

    # Calculate risk score using weighted formula from spec
    # risk_score = 40 * normalize(runway) + 30 * normalize(stability) + 30 * savings_ratio
    runway_normalized = normalize(min(runway_months, 12.0), 0.0, 12.0)
    stability_normalized = normalize(stability_ratio, 0.5, 2.0)

    risk_score = int(
        40 * runway_normalized * 100
        + 30 * stability_normalized * 100
        + 30 * savings_ratio * 100
    )
    risk_score = max(0, min(100, risk_score))

    # Determine risk label
    if risk_score >= 70:
        risk_label = "Low"
    elif risk_score >= 40:
        risk_label = "Moderate"
    else:
        risk_label = "High"

    return {
        "burn_rate": burn_rate,
        "runway_months": min(runway_months, 999.9),
        "stability_ratio": round(stability_ratio, 2),
        "savings_ratio": round(savings_ratio, 2),
        "risk_score": risk_score,
        "risk_label": risk_label,
    }
