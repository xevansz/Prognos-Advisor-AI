from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin, generate_uuid
from models.enums import AuditAction, AuditResourceType


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_log"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    action: Mapped[AuditAction] = mapped_column(nullable=False)
    resource_type: Mapped[AuditResourceType] = mapped_column(nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String, nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
