from fastapi import APIRouter, Request, status

from api.deps import CurrentUserDep, DbDep
from core.rate_limiter import READ_LIMIT, WRITE_LIMIT, limiter
from schemas.profile import ProfileOut, ProfileUpdate
from services import profile_service

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=ProfileOut | None)
@limiter.limit(READ_LIMIT)
async def get_profile(
    request: Request,
    db: DbDep,
    current_user: CurrentUserDep,
) -> ProfileOut | None:
    """
    Return the current user's profile, or null if not yet created.
    """
    profile = await profile_service.get_profile(db, current_user.user_id)
    return profile


@router.put("", response_model=ProfileOut, status_code=status.HTTP_200_OK)
@limiter.limit(WRITE_LIMIT)
async def upsert_profile(
    request: Request,
    payload: ProfileUpdate,
    db: DbDep,
    current_user: CurrentUserDep,
) -> ProfileOut:
    """
    Create or update the current user's profile.
    """
    profile = await profile_service.upsert_profile(db, current_user.user_id, payload, current_user.display_name)
    return profile
