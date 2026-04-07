from fastapi import APIRouter, Request, status

from api.deps import CurrentUserDep, DbDep
from core.rate_limiter import READ_LIMIT, WRITE_LIMIT, limiter
from schemas.account import AccountCreate, AccountOut, AccountUpdate
from services import account_service

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountOut])
@limiter.limit(READ_LIMIT)
async def list_accounts(
    request: Request,
    db: DbDep,
    current_user: CurrentUserDep,
) -> list[AccountOut]:
    """
    Get all accounts for the current user.
    """
    accounts = await account_service.list_accounts(db, current_user.user_id)
    return accounts


@router.post("", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
@limiter.limit(WRITE_LIMIT)
async def create_account(
    request: Request,
    payload: AccountCreate,
    db: DbDep,
    current_user: CurrentUserDep,
) -> AccountOut:
    """
    Create a new account.
    """
    account = await account_service.create_account(db, current_user.user_id, payload)
    return account


@router.get("/{account_id}", response_model=AccountOut)
@limiter.limit(READ_LIMIT)
async def get_account(
    request: Request,
    account_id: str,
    db: DbDep,
    current_user: CurrentUserDep,
) -> AccountOut:
    """
    Get a specific account.
    """
    account = await account_service.get_account(db, account_id, current_user.user_id)
    return account


@router.put("/{account_id}", response_model=AccountOut)
@limiter.limit(WRITE_LIMIT)
async def update_account(
    request: Request,
    account_id: str,
    payload: AccountUpdate,
    db: DbDep,
    current_user: CurrentUserDep,
) -> AccountOut:
    """
    Update an account's metadata.
    """
    account = await account_service.update_account(db, account_id, current_user.user_id, payload)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(WRITE_LIMIT)
async def delete_account(
    request: Request,
    account_id: str,
    db: DbDep,
    current_user: CurrentUserDep,
) -> None:
    """
    Delete an account.
    """
    await account_service.delete_account(db, account_id, current_user.user_id)
