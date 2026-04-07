from datetime import date

from fastapi import APIRouter, Query, Request, status

from api.deps import CurrentUserDep, DbDep
from core.rate_limiter import READ_LIMIT, WRITE_LIMIT, limiter
from schemas.transaction import TransactionCreate, TransactionOut, TransactionUpdate
from services import transaction_service

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut])
@limiter.limit(READ_LIMIT)
async def list_transactions(
    request: Request,
    db: DbDep,
    current_user: CurrentUserDep,
    account_id: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> list[TransactionOut]:
    """
    Get transactions for the current user with optional filters.
    """
    transactions = await transaction_service.list_transactions(
        db, current_user.user_id, account_id, from_date, to_date, limit, offset
    )
    return transactions


@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
@limiter.limit(WRITE_LIMIT)
async def create_transaction(
    request: Request,
    payload: TransactionCreate,
    db: DbDep,
    current_user: CurrentUserDep,
) -> TransactionOut:
    """
    Create a new transaction and update account balance.
    """
    transaction = await transaction_service.create_transaction(db, current_user.user_id, payload)
    return transaction


@router.get("/{transaction_id}", response_model=TransactionOut)
@limiter.limit(READ_LIMIT)
async def get_transaction(
    request: Request,
    transaction_id: str,
    db: DbDep,
    current_user: CurrentUserDep,
) -> TransactionOut:
    """
    Get a specific transaction.
    """
    transaction = await transaction_service.get_transaction(db, transaction_id, current_user.user_id)
    return transaction


@router.put("/{transaction_id}", response_model=TransactionOut)
@limiter.limit(WRITE_LIMIT)
async def update_transaction(
    request: Request,
    transaction_id: str,
    payload: TransactionUpdate,
    db: DbDep,
    current_user: CurrentUserDep,
) -> TransactionOut:
    """
    Update a transaction and adjust balances.
    """
    transaction = await transaction_service.update_transaction(db, transaction_id, current_user.user_id, payload)
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(WRITE_LIMIT)
async def delete_transaction(
    request: Request,
    transaction_id: str,
    db: DbDep,
    current_user: CurrentUserDep,
) -> None:
    """
    Delete a transaction and revert balance changes.
    """
    await transaction_service.delete_transaction(db, transaction_id, current_user.user_id)
