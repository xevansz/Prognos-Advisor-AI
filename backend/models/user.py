from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    Shadow user table keyed by Supabase user id.
    
    The id field IS the Supabase user.id (not a separate field).
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
    )
    email: Mapped[str | None] = mapped_column(String, nullable=True)
