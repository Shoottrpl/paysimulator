import uuid
from datetime import datetime, timedelta, timezone

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from database.models.token import RefreshToken, RevokedToken
from settings import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_jwt_token(
        user_data: dict,
        token_type: str = "access",
        access_exp_seconds: int = settings.jwt_access_token_expiration,
        refresh_exp_seconds: int = settings.jwt_refresh_token_expiration
) -> str:
    expiration = (
        access_exp_seconds
        if token_type == "access"
        else refresh_exp_seconds
    )

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_data["user_id"]),
        "full_name": user_data["full_name"],
        "email": user_data["email"],
        "role": user_data["role"],
        "type": token_type,
        "exp": now + timedelta(seconds=expiration),
        "iat": now,
        "jti": str(uuid.uuid4()),
    }

    return jwt.encode(
        payload,
        settings.private_key.get_secret_value(),
        algorithm=settings.algorithm,
        headers={"typ": "JWT"},
    )


async def decode_jwt_token(token: str, session: AsyncSession) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.public_key,
            algorithms=[settings.algorithm],
            options={"require": ["exp", "iat", "sub", "jti"]},
        )

        if payload.get("type") not in ["access", "refresh"]:
            raise InvalidTokenError("Invalid token type")

        if "jti" not in payload:
            raise InvalidTokenError("Missing token ID")

        if await is_token_revoked(payload["jti"], session):
            raise InvalidTokenError("Token revoked")

        return payload

    except ExpiredSignatureError:
        raise ExpiredSignatureError("Token expired")
    except Exception as e:
        raise InvalidTokenError(f"Invalid token: {str(e)}")


async def is_token_revoked(jti: str, session: AsyncSession) -> bool:
    query = select(exists().where(RevokedToken.jti == jti))
    return bool(await session.scalar(query))


async def revoked_token(user: dict, token_type, jti: str, expires_at, session: AsyncSession):
    if not await is_token_revoked(jti, session):
        revoked_token = RevokedToken(user_id=user["id"], token_type=token_type,jti=jti, expires_at=expires_at)
        session.add(revoked_token)


async def store_refresh_token(user_id: int, refresh_token: str, session: AsyncSession):
    await delete_refresh_tokens(user_id, session)

    hashed_token = pwd_context.hash(refresh_token)

    new_token = RefreshToken(
        user_id=user_id,
        token=hashed_token,
        expires_at=datetime.now()
        + timedelta(seconds=settings.jwt_refresh_token_expiration),
    )
    session.add(new_token)


async def retrieve_refresh_token(user_id, session: AsyncSession):
    token = await session.scalar(
        select(RefreshToken.token)
        .where(RefreshToken.user_id == user_id)
        .where(RefreshToken.is_active)
    )
    return token


async def delete_refresh_tokens(user_id: int, session: AsyncSession):
    await session.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))
