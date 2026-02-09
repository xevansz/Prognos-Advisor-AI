from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import Optional

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
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    target_amount: Optional[Decimal] = Field(default=None, gt=0)
    target_currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    target_date: Optional[date_type] = None
    priority: Optional[GoalPriority] = None


class GoalOut(GoalBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
