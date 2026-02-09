from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from models.enums import AccountType


class AccountBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: AccountType
    currency: str = Field(min_length=3, max_length=3)


class AccountCreate(AccountBase):
    initial_balance: Decimal | None = Field(default=None, ge=0)


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    type: AccountType | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)


class AccountOut(AccountBase):
    id: str
    user_id: str
    balance: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
