from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin, generate_uuid
from models.enums import TransactionType


class Transaction(Base, TimestampMixin):
    """
    Single-entry transactions (debits and credits).
    """

    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=generate_uuid,
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    account_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        index=True,
    )

    label: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, native_enum=False, length=10),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_rule_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("recurrence_rules.id", ondelete="SET NULL"),
        nullable=True,
    )
