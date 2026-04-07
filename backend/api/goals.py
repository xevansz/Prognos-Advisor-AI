from fastapi import APIRouter, Request, status

from api.deps import CurrentUserDep, DbDep
from core.rate_limiter import READ_LIMIT, WRITE_LIMIT, limiter
from schemas.goal import GoalCreate, GoalOut, GoalUpdate
from services import goal_service

router = APIRouter(prefix="/api/goals", tags=["goals"])


@router.get("", response_model=list[GoalOut])
@limiter.limit(READ_LIMIT)
async def list_goals(
    request: Request,
    db: DbDep,
    current_user: CurrentUserDep,
) -> list[GoalOut]:
    """
    Get all goals for the current user.
    """
    goals = await goal_service.list_goals(db, current_user.user_id)
    return goals


@router.post("", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
@limiter.limit(WRITE_LIMIT)
async def create_goal(
    request: Request,
    payload: GoalCreate,
    db: DbDep,
    current_user: CurrentUserDep,
) -> GoalOut:
    """
    Create a new goal.
    """
    goal = await goal_service.create_goal(db, current_user.user_id, payload)
    return goal


@router.get("/{goal_id}", response_model=GoalOut)
@limiter.limit(READ_LIMIT)
async def get_goal(
    request: Request,
    goal_id: str,
    db: DbDep,
    current_user: CurrentUserDep,
) -> GoalOut:
    """
    Get a specific goal.
    """
    goal = await goal_service.get_goal(db, goal_id, current_user.user_id)
    return goal


@router.put("/{goal_id}", response_model=GoalOut)
@limiter.limit(WRITE_LIMIT)
async def update_goal(
    request: Request,
    goal_id: str,
    payload: GoalUpdate,
    db: DbDep,
    current_user: CurrentUserDep,
) -> GoalOut:
    """
    Update a goal.
    """
    goal = await goal_service.update_goal(db, goal_id, current_user.user_id, payload)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(WRITE_LIMIT)
async def delete_goal(
    request: Request,
    goal_id: str,
    db: DbDep,
    current_user: CurrentUserDep,
) -> None:
    """
    Delete a goal.
    """
    await goal_service.delete_goal(db, goal_id, current_user.user_id)
