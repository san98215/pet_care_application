from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Auxiliary category + weight pair stored in User.priorities (mental is always weighted separately)
class PriorityWeight(BaseModel):
    category: str
    weight: float = Field(ge=0.0, le=1.0)


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: str | None = None


class UserRead(UserBase):
    # `from_attributes` lets this be built directly from a user in the database
    model_config = ConfigDict(from_attributes=True)

    # validates response fields against the model and ensures hashed passwords
    # are not returned
    id: int
    priorities: list[PriorityWeight]
    created_at: datetime


class PrioritiesUpdate(BaseModel):
    priorities: list[PriorityWeight]


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
