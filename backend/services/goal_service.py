from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Goal
from schemas.goal import GoalCreate, GoalUpdate


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
    await db.commit()
    await db.refresh(goal)

    return goal


async def update_goal(
    db: AsyncSession, goal_id: str, user_id: str, payload: GoalUpdate
) -> Goal:
    """
    Update a goal.
    """
    goal = await get_goal(db, goal_id, user_id)

    if payload.name is not None:
        goal.name = payload.name
    if payload.target_amount is not None:
        goal.target_amount = payload.target_amount
    if payload.target_currency is not None:
        goal.target_currency = payload.target_currency.upper()
    if payload.target_date is not None:
        goal.target_date = payload.target_date
    if payload.priority is not None:
        goal.priority = payload.priority

    await db.commit()
    await db.refresh(goal)

    return goal


async def delete_goal(db: AsyncSession, goal_id: str, user_id: str) -> None:
    """
    Delete a goal.
    """
    goal = await get_goal(db, goal_id, user_id)
    await db.delete(goal)
    await db.commit()
