from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt

from config import settings


class CurrentUser:
    """
    Minimal representation of the authenticated user.

    For MVP we only need the Supabase `user_id` (subject) to scope all queries.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id


async def get_current_user(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> CurrentUser:
    """
    Extract the current user from a Supabase-issued JWT.

    NOTE: For now this performs basic decoding and subject extraction.
    Signature / issuer / audience validation should be added once the
    Supabase JWKS and configuration values are available.
    """

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    token = authorization.removeprefix("Bearer ").strip()

    try:
        # TODO: Add full verification using Supabase JWKS, issuer, and audience.
        payload = jwt.get_unverified_claims(token)  # type: ignore[attr-defined]
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not decode access token",
        )

    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
        )

    return CurrentUser(user_id=user_id)


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]

