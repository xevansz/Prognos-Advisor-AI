from datetime import date, datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Account, RecurrenceRule, Transaction
from models.enums import RecurrenceFrequency, TransactionType
from schemas.transaction import TransactionCreate, TransactionUpdate


async def list_transactions(
    db: AsyncSession,
    user_id: str,
    account_id: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Transaction]:
    """
    Get transactions for a user with optional filters.
    """
    stmt = select(Transaction).where(Transaction.user_id == user_id)

    if account_id:
        stmt = stmt.where(Transaction.account_id == account_id)
    if from_date:
        stmt = stmt.where(Transaction.date >= from_date)
    if to_date:
        stmt = stmt.where(Transaction.date <= to_date)

    stmt = stmt.order_by(Transaction.date.desc()).limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_transaction(
    db: AsyncSession, transaction_id: str, user_id: str
) -> Transaction:
    """
    Get a specific transaction, ensuring it belongs to the user.
    """
    stmt = select(Transaction).where(
        Transaction.id == transaction_id, Transaction.user_id == user_id
    )
    result = await db.execute(stmt)
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    return transaction


async def _update_account_balance(
    db: AsyncSession,
    account: Account,
    amount: Decimal,
    transaction_type: TransactionType,
    is_reversal: bool = False,
) -> None:
    """
    Update account balance based on transaction type.
    """
    if is_reversal:
        if transaction_type == TransactionType.CREDIT:
            account.balance -= amount
        else:
            account.balance += amount
    else:
        if transaction_type == TransactionType.CREDIT:
            account.balance += amount
        else:
            account.balance -= amount


async def create_transaction(
    db: AsyncSession, user_id: str, payload: TransactionCreate
) -> Transaction:
    """
    Create a new transaction and update account balance atomically.
    """
    stmt = select(Account).where(
        Account.id == payload.account_id, Account.user_id == user_id
    )
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    currency = payload.currency or account.currency

    transaction = Transaction(
        user_id=user_id,
        account_id=payload.account_id,
        label=payload.label,
        description=payload.description,
        date=payload.date,
        amount=payload.amount,
        type=payload.type,
        currency=currency.upper(),
        is_recurring=payload.is_recurring,
    )

    if payload.is_recurring:
        recurrence_rule = RecurrenceRule(
            user_id=user_id,
            frequency=RecurrenceFrequency.MONTHLY,
            day_of_month=payload.date.day,
            start_date=payload.date,
            active=True,
        )
        db.add(recurrence_rule)
        await db.flush()
        transaction.recurrence_rule_id = recurrence_rule.id

    await _update_account_balance(db, account, payload.amount, payload.type)

    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    return transaction


async def update_transaction(
    db: AsyncSession, transaction_id: str, user_id: str, payload: TransactionUpdate
) -> Transaction:
    """
    Update a transaction and adjust account balances accordingly.
    """
    transaction = await get_transaction(db, transaction_id, user_id)

    stmt = select(Account).where(
        Account.id == transaction.account_id, Account.user_id == user_id
    )
    result = await db.execute(stmt)
    old_account = result.scalar_one_or_none()

    if not old_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    await _update_account_balance(
        db, old_account, transaction.amount, transaction.type, is_reversal=True
    )

    if payload.label is not None:
        transaction.label = payload.label
    if payload.description is not None:
        transaction.description = payload.description
    if payload.date is not None:
        transaction.date = payload.date
    if payload.amount is not None:
        transaction.amount = payload.amount
    if payload.type is not None:
        transaction.type = payload.type

    if payload.account_id is not None and payload.account_id != transaction.account_id:
        stmt = select(Account).where(
            Account.id == payload.account_id, Account.user_id == user_id
        )
        result = await db.execute(stmt)
        new_account = result.scalar_one_or_none()

        if not new_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New account not found",
            )

        transaction.account_id = payload.account_id
        await _update_account_balance(db, new_account, transaction.amount, transaction.type)
    else:
        await _update_account_balance(db, old_account, transaction.amount, transaction.type)

    await db.commit()
    await db.refresh(transaction)

    return transaction


async def delete_transaction(
    db: AsyncSession, transaction_id: str, user_id: str
) -> None:
    """
    Delete a transaction and revert its effect on account balance.
    """
    transaction = await get_transaction(db, transaction_id, user_id)

    stmt = select(Account).where(
        Account.id == transaction.account_id, Account.user_id == user_id
    )
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()

    if account:
        await _update_account_balance(
            db, account, transaction.amount, transaction.type, is_reversal=True
        )

    await db.delete(transaction)
    await db.commit()
