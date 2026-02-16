from datetime import datetime, timedelta
from decimal import Decimal

from core.logging import get_logger

logger = get_logger(__name__)


def compute_risk_metrics(
    transactions: list[dict],
    liquid_accounts: list[dict],
    base_currency: str,
) -> dict:
    """
    Compute risk metrics: burn rate, runway, and risk capacity score.
    
    Args:
        transactions: List of transaction dicts with 'amount', 'type', 'date'
        liquid_accounts: List of account dicts with 'balance' (in base currency)
        base_currency: User's base currency
        
    Returns:
        Dict with burn_rate, runway_months, risk_capacity_score
    """
    
    if not transactions:
        total_liquid = sum(Decimal(str(acc.get("balance", 0))) for acc in liquid_accounts)
        return {
            "burn_rate": 0.0,
            "runway_months": float("inf") if total_liquid > 0 else 0.0,
            "risk_capacity_score": 50,
        }
    
    cutoff_date = datetime.utcnow().date() - timedelta(days=60)
    recent_transactions = [
        tx for tx in transactions 
        if tx.get("date") and tx["date"] >= cutoff_date
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
    
    if runway_months >= 12:
        risk_capacity_score = 90
    elif runway_months >= 6:
        risk_capacity_score = 70
    elif runway_months >= 3:
        risk_capacity_score = 50
    elif runway_months >= 1:
        risk_capacity_score = 30
    else:
        risk_capacity_score = 10
    
    return {
        "burn_rate": burn_rate,
        "runway_months": min(runway_months, 999.9),
        "risk_capacity_score": risk_capacity_score,
    }
