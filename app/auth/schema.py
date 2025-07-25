import re

from pydantic import (BaseModel, EmailStr, Field, SecretStr, ValidationInfo,
                      field_validator)

from app.auth.role import Role


class PasswordMixin:
    @field_validator("password")
    def validate_password_strength(cls, v: SecretStr) -> SecretStr:
        password = v.get_secret_value()

        if len(password) < 8:
            raise ValueError("Длина пароля должна быть более 8 символов")

        if not any(c.isupper() for c in password):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")

        if not any(c.isdigit() for c in password):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Пароль должен содержать хотя бы один специальный символ")

        return v

    @field_validator("password_confirm")
    def validate_confirm_password(cls, v: SecretStr, info: ValidationInfo) -> SecretStr:
        main_field = info.field_name.replace("_confirm", "")

        if main_field not in info.data:
            raise ValueError(f"Поле {main_field} отсутствует")

        if v.get_secret_value() != info.data[main_field].get_secret_value():
            raise ValueError("Пароли не совпадают")

        return v


class UserCreate(BaseModel, PasswordMixin):
    email: EmailStr
    password: SecretStr
    password_confirm: SecretStr
    full_name: str
    role: Role = Field(default=Role.USER)


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: SecretStr


class ResetPasswordRequestSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel, PasswordMixin):
    token: str
    password: SecretStr
    password_confirm: SecretStr
