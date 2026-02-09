from datetime import datetime

from pydantic import BaseModel, Field

from models.enums import RiskAppetite


class ProfileBase(BaseModel):
    age: int = Field(ge=0, description="User age in years")
    display_name: str | None = None
    gender: str | None = None
    base_currency: str = Field(min_length=3, max_length=3)
    risk_appetite: RiskAppetite


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
