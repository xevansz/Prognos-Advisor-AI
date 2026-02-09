from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Profile, User
from schemas.profile import ProfileCreate, ProfileUpdate


async def get_or_create_user(db: AsyncSession, user_id: str) -> User:
    """
    Ensure there is a shadow `users` row for the Supabase user.
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        user = User(id=user_id)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def get_profile(db: AsyncSession, user_id: str) -> Profile | None:
    """
    Get the profile for a user.
    """
    await get_or_create_user(db, user_id)

    stmt = select(Profile).where(Profile.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def upsert_profile(
    db: AsyncSession, user_id: str, payload: ProfileCreate | ProfileUpdate
) -> Profile:
    """
    Create or update a user's profile.
    """
    user = await get_or_create_user(db, user_id)

    stmt = select(Profile).where(Profile.user_id == user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if profile is None:
        profile = Profile(
            user_id=user.id,
            age=payload.age,
            display_name=payload.display_name,
            gender=payload.gender,
            base_currency=payload.base_currency.upper(),
            risk_appetite=payload.risk_appetite,
        )
        db.add(profile)
    else:
        profile.age = payload.age
        profile.display_name = payload.display_name
        profile.gender = payload.gender
        profile.base_currency = payload.base_currency.upper()
        profile.risk_appetite = payload.risk_appetite

    await db.commit()
    await db.refresh(profile)

    return profile
