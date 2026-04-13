from functools import lru_cache
from typing import Annotated

import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from core.config import settings

security = HTTPBearer()


# Cache for JWKS (public keys)
@lru_cache(maxsize=1)
def get_jwks():
    """Fetch and cache Supabase public keys for ES256 verification."""
    if not settings.supabase_jwks_url:
        return None

    jwks_url = settings.supabase_jwks_url
    try:
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Warning: Failed to fetch JWKS: {e}")
        return None


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
        # First, decode header to check algorithm
        unverified_header = jwt.get_unverified_header(token)
        algorithm = unverified_header.get("alg")

        if algorithm == "HS256":
            # HS256 (email/password): verify with JWT secret
            if not settings.supabase_jwt_secret:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="JWT secret not configured",
                )
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience=settings.supabase_jwt_audience,
                issuer=settings.supabase_jwt_issuer,
            )
        elif algorithm == "ES256":
            # ES256 (OAuth): verify with public key from JWKS
            jwks = get_jwks()
            if not jwks:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to fetch public keys for token verification",
                )

            # Find the matching key by kid
            kid = unverified_header.get("kid")
            public_key = None
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    public_key = key
                    break

            if not public_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Public key not found for token",
                )

            payload = jwt.decode(
                token,
                public_key,
                algorithms=["ES256"],
                audience=settings.supabase_jwt_audience,
                issuer=settings.supabase_jwt_issuer,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unsupported token algorithm: {algorithm}",
            )
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
