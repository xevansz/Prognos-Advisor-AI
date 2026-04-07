from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Account, AuditAction, AuditResourceType, Transaction
from schemas.account import AccountCreate, AccountUpdate
from services.audit_service import log_audit


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


async def create_account(db: AsyncSession, user_id: str, payload: AccountCreate) -> Account:
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
    await log_audit(
        db,
        user_id=user_id,
        action=AuditAction.CREATE,
        resource_type=AuditResourceType.ACCOUNT,
        resource_id=str(account.id),
        details={
            "name": account.name,
            "type": account.type,
            "currency": account.currency,
            "balance": str(account.balance),
        },
    )
    await db.commit()
    await db.refresh(account)

    return account


async def update_account(db: AsyncSession, account_id: str, user_id: str, payload: AccountUpdate) -> Account:
    """
    Update an account's metadata (not balance).
    """
    account = await get_account(db, account_id, user_id)

    # Track changes for audit
    changes = {}
    if payload.name is not None:
        changes["name"] = {"old": account.name, "new": payload.name}
        account.name = payload.name
    if payload.type is not None:
        changes["type"] = {"old": account.type, "new": payload.type}
        account.type = payload.type
    if payload.currency is not None:
        changes["currency"] = {"old": account.currency, "new": payload.currency.upper()}
        account.currency = payload.currency.upper()

    if changes:
        await log_audit(
            db,
            user_id=user_id,
            action=AuditAction.UPDATE,
            resource_type=AuditResourceType.ACCOUNT,
            resource_id=account_id,
            details=changes,
        )

    await db.commit()
    await db.refresh(account)

    return account


async def delete_account(db: AsyncSession, account_id: str, user_id: str) -> None:
    """
    Delete an account.

    Prevents deletion if the account has associated transactions to maintain data integrity.
    """
    account = await get_account(db, account_id, user_id)

    # Check if account has any transactions
    stmt = select(Transaction).where(Transaction.account_id == account_id).limit(1)
    result = await db.execute(stmt)
    has_transactions = result.scalar_one_or_none() is not None

    if has_transactions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete account with existing transactions. Please delete all transactions first.",
        )

    await log_audit(
        db,
        user_id=user_id,
        action=AuditAction.DELETE,
        resource_type=AuditResourceType.ACCOUNT,
        resource_id=account_id,
        details={"name": account.name, "type": account.type, "balance": str(account.balance)},
    )
    await db.delete(account)
    await db.commit()
