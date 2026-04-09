from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from core.config import settings

security = HTTPBearer()


class CurrentUser:
    """
    For MVP we only need the Supabase `user_id` (subject) to scope all queries.
    """

    def __init__(self, user_id: str, display_name: str | None = None):
        self.user_id = user_id
        self.display_name = display_name


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> CurrentUser:
    """
    Extract the current user from a Supabase-issued JWT.

    Verifies JWT signature if supabase_jwt_secret is configured,
    otherwise falls back to unverified claims (development only).
    """

    token = credentials.credentials

    try:
        # If JWT secret is configured, verify the signature
        if settings.supabase_jwt_secret:
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience=settings.supabase_jwt_audience,
                issuer=settings.supabase_jwt_issuer,
            )
        else:
            # Development fallback - ONLY FOR DEVLOPMENT
            payload = jwt.get_unverified_claims(token)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        ) from e

    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
        )

    user_metadata = payload.get("user_metadata", {})
    display_name = user_metadata.get("display_name")

    return CurrentUser(user_id=user_id, display_name=display_name)


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
