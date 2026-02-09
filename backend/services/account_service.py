from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Account
from schemas.account import AccountCreate, AccountUpdate


async def list_accounts(db: AsyncSession, user_id: str) -> list[Account]:
    """
    Get all accounts for a user.
    """
    stmt = select(Account).where(Account.user_id == user_id).order_by(Account.created_at)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_account(db: AsyncSession, account_id: str, user_id: str) -> Account:
    """
    Get a specific account, ensuring it belongs to the user.
    """
    stmt = select(Account).where(Account.id == account_id, Account.user_id == user_id)
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    return account


async def create_account(
    db: AsyncSession, user_id: str, payload: AccountCreate
) -> Account:
    """
    Create a new account for a user.
    """
    initial_balance = payload.initial_balance or Decimal("0")

    account = Account(
        user_id=user_id,
        name=payload.name,
        type=payload.type,
        currency=payload.currency.upper(),
        balance=initial_balance,
    )

    db.add(account)
    await db.commit()
    await db.refresh(account)

    return account


async def update_account(
    db: AsyncSession, account_id: str, user_id: str, payload: AccountUpdate
) -> Account:
    """
    Update an account's metadata (not balance).
    """
    account = await get_account(db, account_id, user_id)

    if payload.name is not None:
        account.name = payload.name
    if payload.type is not None:
        account.type = payload.type
    if payload.currency is not None:
        account.currency = payload.currency.upper()

    await db.commit()
    await db.refresh(account)

    return account


async def delete_account(db: AsyncSession, account_id: str, user_id: str) -> None:
    """
    Delete an account.
    """
    account = await get_account(db, account_id, user_id)
    await db.delete(account)
    await db.commit()
