import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from models import Account, AuditLog, Goal, Profile, PrognosisReport, PrognosisUsage, Transaction, User


async def verify_password_with_supabase(email: str, password: str) -> bool:
    """
    Verify user password with Supabase Auth API.

    Returns True if password is correct, False otherwise.
    """
    # Supabase Auth endpoint for password verification
    # This uses the signInWithPassword endpoint to verify credentials
    supabase_url = settings.supabase_jwt_issuer.replace("/auth/v1", "") if settings.supabase_jwt_issuer else None

    if not supabase_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase configuration not found",
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{supabase_url}/auth/v1/token?grant_type=password",
                json={"email": email, "password": password},
                headers={"apikey": settings.supabase_jwt_secret or ""},
                timeout=10.0,
            )
            return response.status_code == 200
    except Exception:
        return False


async def delete_user_account(db: AsyncSession, user_id: str, user_email: str, password: str) -> None:
    """
    Delete a user account and all associated data.

    Requires password verification for security.
    Cascade deletes:
    - All transactions
    - All accounts
    - All goals
    - Profile
    - Prognosis reports and usage records
    - Audit logs
    - User record

    Args:
        db: Database session
        user_id: User ID to delete
        user_email: User email for password verification
        password: User password for verification

    Raises:
        HTTPException: If password verification fails or deletion fails
    """
    # Verify password first
    password_valid = await verify_password_with_supabase(user_email, password)
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password. Account deletion cancelled.",
        )

    # Verify user exists
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        # Delete in order to respect foreign key constraints

        # 1. Delete transactions (references accounts)
        stmt = select(Transaction).where(Transaction.user_id == user_id)
        result = await db.execute(stmt)
        transactions = result.scalars().all()
        for transaction in transactions:
            await db.delete(transaction)

        # 2. Delete accounts
        stmt = select(Account).where(Account.user_id == user_id)
        result = await db.execute(stmt)
        accounts = result.scalars().all()
        for account in accounts:
            await db.delete(account)

        # 3. Delete goals
        stmt = select(Goal).where(Goal.user_id == user_id)
        result = await db.execute(stmt)
        goals = result.scalars().all()
        for goal in goals:
            await db.delete(goal)

        # 4. Delete profile
        stmt = select(Profile).where(Profile.user_id == user_id)
        result = await db.execute(stmt)
        profile = result.scalar_one_or_none()
        if profile:
            await db.delete(profile)

        # 5. Delete prognosis reports
        stmt = select(PrognosisReport).where(PrognosisReport.user_id == user_id)
        result = await db.execute(stmt)
        reports = result.scalars().all()
        for report in reports:
            await db.delete(report)

        # 6. Delete prognosis usage records
        stmt = select(PrognosisUsage).where(PrognosisUsage.user_id == user_id)
        result = await db.execute(stmt)
        usages = result.scalars().all()
        for usage in usages:
            await db.delete(usage)

        # 7. Delete audit logs
        stmt = select(AuditLog).where(AuditLog.user_id == user_id)
        result = await db.execute(stmt)
        audit_logs = result.scalars().all()
        for log in audit_logs:
            await db.delete(log)

        # 8. Finally, delete the user record
        await db.delete(user)

        # Commit all deletions
        await db.commit()

    except Exception as e:
        # Rollback on any error
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}",
        ) from e
