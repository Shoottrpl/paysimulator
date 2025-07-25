from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.auth.role import Role


class User(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: Role = Field(default=Role.USER)


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[Role] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str

    model_config = ConfigDict(from_attributes=True)
