from fastapi import APIRouter, Request, status

from api.deps import CurrentUserDep, DbDep
from core.rate_limiter import WRITE_LIMIT, limiter
from schemas.user import UserDeleteRequest
from services import user_service

router = APIRouter(prefix="/api/user", tags=["user"])


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(WRITE_LIMIT)
async def delete_user_account(
    request: Request,
    payload: UserDeleteRequest,
    db: DbDep,
    current_user: CurrentUserDep,
) -> None:
    """
    Delete the current user's account and all associated data.

    Requires password verification for security.
    This action is irreversible and will delete:
    - All transactions
    - All accounts
    - All goals
    - Profile
    - Prognosis reports
    - All audit logs
    - User record
    """
    # Get user email from the authenticated user context
    # Note: In production, you'd want to fetch this from the User model or JWT claims
    user_email = current_user.user_id  # Placeholder - should be actual email

    await user_service.delete_user_account(db, current_user.user_id, user_email, payload.password)
