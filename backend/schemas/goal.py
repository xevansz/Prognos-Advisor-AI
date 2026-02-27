from datetime import date as date_type
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from models.enums import GoalPriority


class GoalBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    target_amount: Decimal = Field(gt=0)
    target_currency: str = Field(min_length=3, max_length=3)
    target_date: date_type
    priority: GoalPriority


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    target_amount: Decimal | None = Field(default=None, gt=0)
    target_currency: str | None = Field(default=None, min_length=3, max_length=3)
    target_date: date_type | None = None
    priority: GoalPriority | None = None


class GoalOut(GoalBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
