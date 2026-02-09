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

    def __init__(self, user_id: str):
        self.user_id = user_id


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> CurrentUser:
    """
    Extract the current user from a Supabase-issued JWT.

    For MVP, performs basic decoding and subject extraction.
    Full signature verification with JWKS should be added in production.
    """

    token = credentials.credentials

    try:
        payload = jwt.get_unverified_claims(token)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not decode access token: {str(e)}",
        )

    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
        )

    return CurrentUser(user_id=user_id)


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
