from typing import Optional

from passlib.hash import pbkdf2_sha256
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.model_service import UserService


class AuthService:
    @staticmethod
    def hash_password(password: SecretStr) -> str:
        raw_password = password.get_secret_value()
        return pbkdf2_sha256.hash(raw_password)

    async def authenticate(
        email: str, password: SecretStr, session: AsyncSession
    ) -> Optional[dict]:
        user = await UserService.get_by_email(email, session)

        if user and pbkdf2_sha256.verify(
            password.get_secret_value(), user.password_hash
        ):
            return {
                "user_id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
            }
        return None
