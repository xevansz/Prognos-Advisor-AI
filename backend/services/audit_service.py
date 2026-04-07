from sqlalchemy.ext.asyncio import AsyncSession

from models import AuditAction, AuditLog, AuditResourceType


async def log_audit(
    db: AsyncSession,
    user_id: str,
    action: AuditAction,
    resource_type: AuditResourceType,
    resource_id: str,
    details: dict | None = None,
    ip_address: str | None = None,
) -> None:
    """
    Log an audit event for financial operations.
    
    Args:
        db: Database session
        user_id: User performing the action
        action: Type of action (CREATE, UPDATE, DELETE)
        resource_type: Type of resource (ACCOUNT, TRANSACTION, GOAL, PROFILE)
        resource_id: ID of the resource
        details: Optional dict with before/after values or other context
        ip_address: Optional IP address of the request
    """
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
    )
    
    db.add(audit_log)
    # Note: Caller is responsible for committing the transaction
    # This allows audit logs to be part of the same transaction as the operation
