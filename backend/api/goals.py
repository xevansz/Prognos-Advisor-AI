from fastapi import APIRouter, status

from api.deps import CurrentUserDep, DbDep
from schemas.goal import GoalCreate, GoalOut, GoalUpdate
from services import goal_service

router = APIRouter(prefix="/api/goals", tags=["goals"])


@router.get("", response_model=list[GoalOut])
async def list_goals(
    db: DbDep,
    current_user: CurrentUserDep,
) -> list[GoalOut]:
    """
    Get all goals for the current user.
    """
    goals = await goal_service.list_goals(db, current_user.user_id)
    return goals


@router.post("", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
async def create_goal(
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
async def get_goal(
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
async def update_goal(
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
async def delete_goal(
    goal_id: str,
    db: DbDep,
    current_user: CurrentUserDep,
) -> None:
    """
    Delete a goal.
    """
    await goal_service.delete_goal(db, goal_id, current_user.user_id)
