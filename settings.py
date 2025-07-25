from typing import Optional

from functools import cached_property
from pydantic import SecretStr, FilePath
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.auth.service import AuthService


class Settings(BaseSettings):
    """
    Класс для хранения настроек приложения
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    #db
    user: str
    password: SecretStr
    db: str
    host: str
    port: int

    @property
    def db_url(self) -> str:
        return (f"postgresql+asyncpg://"
                f"{self.user}:{self.password.get_secret_value()}"
                f"@{self.host}:{self.port}/{self.db}")

    # api
    redis_url: str
    sentry_dns: SecretStr
    debug: bool = True

    # service
    secret_key: SecretStr

    #jwt
    algorithm: str
    jwt_access_token_expiration: int
    jwt_refresh_token_expiration: int

    jwt_private_key_path: Optional[FilePath] = None
    jwt_public_key_path: Optional[FilePath] = None

    @cached_property
    def private_key(self) -> SecretStr:
        return SecretStr(self.jwt_private_key_path.read_text())

    @cached_property
    def public_key(self) -> str:
        return self.jwt_public_key_path.read_text()

    test_user_password: str = AuthService.hash_password(
        SecretStr("default_test_password")
    )
    admin_user_password: str = AuthService.hash_password(
        SecretStr("default_admin_password")
    )


settings = Settings()

