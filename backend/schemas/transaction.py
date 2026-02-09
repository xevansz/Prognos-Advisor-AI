from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from models.enums import TransactionType


class TransactionBase(BaseModel):
    label: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    date: date_type
    amount: Decimal = Field(gt=0)
    type: TransactionType


class TransactionCreate(TransactionBase):
    account_id: str
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    is_recurring: bool = False


class TransactionUpdate(BaseModel):
    label: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    date: Optional[date_type] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    type: Optional[TransactionType] = None
    account_id: Optional[str] = None


class TransactionOut(TransactionBase):
    id: str
    user_id: str
    account_id: str
    currency: str
    is_recurring: bool
    recurrence_rule_id: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
