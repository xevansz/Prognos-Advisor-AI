from fastapi import APIRouter, status

from api.deps import CurrentUserDep, DbDep
from schemas.account import AccountCreate, AccountOut, AccountUpdate
from services import account_service

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountOut])
async def list_accounts(
    db: DbDep,
    current_user: CurrentUserDep,
) -> list[AccountOut]:
    """
    Get all accounts for the current user.
    """
    accounts = await account_service.list_accounts(db, current_user.user_id)
    return accounts


@router.post("", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
async def create_account(
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
async def get_account(
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
async def update_account(
    account_id: str,
    payload: AccountUpdate,
    db: DbDep,
    current_user: CurrentUserDep,
) -> AccountOut:
    """
    Update an account's metadata.
    """
    account = await account_service.update_account(
        db, account_id, current_user.user_id, payload
    )
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: str,
    db: DbDep,
    current_user: CurrentUserDep,
) -> None:
    """
    Delete an account.
    """
    await account_service.delete_account(db, account_id, current_user.user_id)
