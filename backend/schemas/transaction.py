from datetime import date as date_type
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from models.enums import TransactionType


class TransactionBase(BaseModel):
    label: str = Field(min_length=1, max_length=255)
    description: str | None = None
    date: date_type
    amount: Decimal = Field(gt=0)
    type: TransactionType


class TransactionCreate(TransactionBase):
    account_id: str
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    is_recurring: bool = False


class TransactionUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    date: date_type | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    type: TransactionType | None = None
    account_id: str | None = None


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
