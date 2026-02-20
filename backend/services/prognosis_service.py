from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.goal_agent import evaluate_goals
from agents.investment_agent import recommend_allocation
from agents.risk_agent import compute_risk_metrics
from core.config import settings
from core.logging import get_logger
from integrations.fx_client import convert_currency
from integrations.llm_client import generate_prognosis_report
from integrations.market_client import get_macro_state
from models import Account, Goal, Profile, PrognosisReport, PrognosisUsage, Transaction
from models.enums import AccountType, TransactionType

logger = get_logger(__name__)


async def check_rate_limit(db: AsyncSession, user_id: str) -> tuple[bool, int]:
    """
    Check if user has exceeded rate limit for prognosis generation.
    
    Returns:
        Tuple of (is_limited, current_count)
    """
    if not settings.prognosis_rate_limit_enabled:
        return False, 0
    
    today = datetime.utcnow().date()
    
    stmt = select(PrognosisUsage).where(
        PrognosisUsage.user_id == user_id,
        PrognosisUsage.date == today,
    )
    result = await db.execute(stmt)
    usage = result.scalar_one_or_none()
    
    if not usage:
        return False, 0
    
    return usage.count >= settings.prognosis_max_requests_per_day, usage.count


async def increment_usage(db: AsyncSession, user_id: str) -> None:
    """
    Increment the prognosis usage count for today.
    """
    today = datetime.utcnow().date()
    
    stmt = select(PrognosisUsage).where(
        PrognosisUsage.user_id == user_id,
        PrognosisUsage.date == today,
    )
    result = await db.execute(stmt)
    usage = result.scalar_one_or_none()
    
    if usage:
        usage.count += 1
    else:
        usage = PrognosisUsage(
            user_id=user_id,
            date=today,
            count=1,
        )
        db.add(usage)
    
    await db.commit()


async def get_cached_report(db: AsyncSession, user_id: str) -> dict | None:
    """
    Get the last cached prognosis report for a user.
    """
    stmt = select(PrognosisReport).where(PrognosisReport.user_id == user_id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()
    
    if not report:
        return None
    
    return {
        "report_json": report.report_json,
        "generated_at": report.generated_at,
        "rate_limited": False,
    }


async def generate_prognosis(db: AsyncSession, user_id: str) -> dict:
    """
    Generate a new prognosis report for a user.
    """
    is_limited, count = await check_rate_limit(db, user_id)
    if is_limited:
        cached = await get_cached_report(db, user_id)
        if cached:
            cached["rate_limited"] = True
            return cached
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {settings.prognosis_max_requests_per_day} reports per day.",
        )
    
    stmt = select(Profile).where(Profile.user_id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile not found. Please create a profile first.",
        )
    
    stmt = select(Account).where(Account.user_id == user_id)
    result = await db.execute(stmt)
    accounts = list(result.scalars().all())
    
    cutoff_date = datetime.utcnow().date() - timedelta(days=60)
    stmt = select(Transaction).where(
        Transaction.user_id == user_id,
        Transaction.date >= cutoff_date,
    )
    result = await db.execute(stmt)
    transactions = list(result.scalars().all())
    
    stmt = select(Goal).where(Goal.user_id == user_id)
    result = await db.execute(stmt)
    goals = list(result.scalars().all())
    
    liquid_accounts = [
        {
            "id": str(acc.id),
            "balance": float(acc.balance),
            "currency": acc.currency,
        }
        for acc in accounts
        if acc.type in [AccountType.BANK, AccountType.CASH]
    ]
    
    transaction_dicts = [
        {
            "id": str(tx.id),
            "amount": float(tx.amount),
            "type": tx.type.value,
            "date": tx.date,
            "currency": tx.currency,
        }
        for tx in transactions
    ]
    
    # Calculate monthly income and savings first
    monthly_debits = Decimal("0")
    monthly_credits = Decimal("0")
    last_30_days = datetime.utcnow().date() - timedelta(days=30)
    
    for tx in transactions:
        if tx.date >= last_30_days:
            if tx.type == TransactionType.DEBIT:
                monthly_debits += tx.amount
            elif tx.type == TransactionType.CREDIT:
                monthly_credits += tx.amount
    
    monthly_income = float(monthly_credits)
    monthly_savings = float(monthly_credits - monthly_debits)
    
    # Compute risk metrics with monthly income
    risk_metrics = compute_risk_metrics(
        transaction_dicts,
        liquid_accounts,
        profile.base_currency,
        monthly_income=monthly_income,
    )
    
    goal_dicts = [
        {
            "id": str(g.id),
            "name": g.name,
            "target_amount": float(g.target_amount),
            "target_date": g.target_date,
            "priority": g.priority.value,
        }
        for g in goals
    ]
    
    # Calculate total current savings (sum of liquid accounts)
    total_current_savings = sum(acc.get("balance", 0) for acc in liquid_accounts)
    
    goal_evaluations = evaluate_goals(
        goal_dicts,
        monthly_savings,
        profile.base_currency,
        current_savings=total_current_savings,
        expected_return=0.07,  # 7% default annual return
    )
    
    macro_state = await get_macro_state()
    
    # Calculate goal time horizon (years to nearest goal)
    goal_time_horizon = 10  # Default
    if goals:
        nearest_goal_months = min(
            max(1, (g.target_date.year - datetime.utcnow().year) * 12 + 
                (g.target_date.month - datetime.utcnow().month))
            for g in goals
        )
        goal_time_horizon = max(1, nearest_goal_months // 12)
    
    allocation = recommend_allocation(
        risk_metrics["risk_score"],
        profile.risk_appetite.value,
        goal_evaluations,
        macro_state,
        age=profile.age,
        goal_time_horizon=goal_time_horizon,
    )
    
    stmt = select(PrognosisReport).where(PrognosisReport.user_id == user_id)
    result = await db.execute(stmt)
    previous_report = result.scalar_one_or_none()
    
    narrator_input = {
        "profile": {
            "age": profile.age,
            "base_currency": profile.base_currency,
            "risk_appetite": profile.risk_appetite.value,
        },
        "risk": risk_metrics,
        "goals": goal_evaluations,
        "allocation": allocation,
        "previous_report": previous_report.report_json if previous_report else None,
    }
    
    report_json = await generate_prognosis_report(narrator_input)
    
    inputs_snapshot = {
        "accounts_count": len(accounts),
        "transactions_count": len(transactions),
        "goals_count": len(goals),
        "generated_at": datetime.utcnow().isoformat(),
    }
    
    if previous_report:
        previous_report.report_json = report_json
        previous_report.inputs_snapshot = inputs_snapshot
        previous_report.generated_at = datetime.utcnow()
    else:
        new_report = PrognosisReport(
            user_id=user_id,
            report_json=report_json,
            inputs_snapshot=inputs_snapshot,
            generated_at=datetime.utcnow(),
        )
        db.add(new_report)
    
    await increment_usage(db, user_id)
    await db.commit()
    
    return {
        "report_json": report_json,
        "generated_at": datetime.utcnow(),
        "rate_limited": False,
    }
