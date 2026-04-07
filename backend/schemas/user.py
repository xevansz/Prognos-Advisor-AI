from pydantic import BaseModel, Field


class UserDeleteRequest(BaseModel):
    password: str = Field(min_length=1, description="User password for verification")
