from pydantic import BaseModel, EmailStr, Field, field_validator

from database.models.user import Role


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    user_id: int
    email: EmailStr
    role: Role = Field(default=Role.USER)
    exp: int
    iat: int

    @field_validator("role")
    def validate_role(cls, role):
        allowed_roles = {"user", "admin"}
        if role not in allowed_roles:
            raise ValueError(f"Недопустимая роль. Допустимые: {allowed_roles}")
        return role
