from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import AuditAction, AuditResourceType, Goal
from schemas.goal import GoalCreate, GoalUpdate
from services.audit_service import log_audit


async def list_goals(db: AsyncSession, user_id: str) -> list[Goal]:
    """
    Get all goals for a user.
    """
    stmt = select(Goal).where(Goal.user_id == user_id).order_by(Goal.target_date)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_goal(db: AsyncSession, goal_id: str, user_id: str) -> Goal:
    """
    Get a specific goal, ensuring it belongs to the user.
    """
    stmt = select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
    result = await db.execute(stmt)
    goal = result.scalar_one_or_none()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    return goal


async def create_goal(db: AsyncSession, user_id: str, payload: GoalCreate) -> Goal:
    """
    Create a new goal for a user.
    """
    goal = Goal(
        user_id=user_id,
        name=payload.name,
        target_amount=payload.target_amount,
        target_currency=payload.target_currency.upper(),
        target_date=payload.target_date,
        priority=payload.priority,
    )

    db.add(goal)
    await log_audit(
        db,
        user_id=user_id,
        action=AuditAction.CREATE,
        resource_type=AuditResourceType.GOAL,
        resource_id=str(goal.id),
        details={"name": goal.name, "target_amount": str(goal.target_amount), "target_date": str(goal.target_date)},
    )
    await db.commit()
    await db.refresh(goal)

    return goal


async def update_goal(db: AsyncSession, goal_id: str, user_id: str, payload: GoalUpdate) -> Goal:
    """
    Update a goal.
    """
    goal = await get_goal(db, goal_id, user_id)

    # Track changes for audit
    changes = {}
    if payload.name is not None:
        changes["name"] = {"old": goal.name, "new": payload.name}
        goal.name = payload.name
    if payload.target_amount is not None:
        changes["target_amount"] = {"old": str(goal.target_amount), "new": str(payload.target_amount)}
        goal.target_amount = payload.target_amount
    if payload.target_currency is not None:
        changes["target_currency"] = {"old": goal.target_currency, "new": payload.target_currency.upper()}
        goal.target_currency = payload.target_currency.upper()
    if payload.target_date is not None:
        changes["target_date"] = {"old": str(goal.target_date), "new": str(payload.target_date)}
        goal.target_date = payload.target_date
    if payload.priority is not None:
        changes["priority"] = {"old": goal.priority, "new": payload.priority}
        goal.priority = payload.priority

    if changes:
        await log_audit(
            db,
            user_id=user_id,
            action=AuditAction.UPDATE,
            resource_type=AuditResourceType.GOAL,
            resource_id=goal_id,
            details=changes,
        )

    await db.commit()
    await db.refresh(goal)

    return goal


async def delete_goal(db: AsyncSession, goal_id: str, user_id: str) -> None:
    """
    Delete a goal.
    """
    goal = await get_goal(db, goal_id, user_id)
    await log_audit(
        db,
        user_id=user_id,
        action=AuditAction.DELETE,
        resource_type=AuditResourceType.GOAL,
        resource_id=goal_id,
        details={"name": goal.name, "target_amount": str(goal.target_amount)},
    )
    await db.delete(goal)
    await db.commit()
