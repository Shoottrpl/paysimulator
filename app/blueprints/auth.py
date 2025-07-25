from jwt import ExpiredSignatureError, InvalidTokenError
from pydantic import SecretStr
from sanic import Blueprint, json
from sanic_ext import openapi

from app.auth.decorators import requires_role
from app.auth.role import Role
from app.auth.service import AuthService
from app.jwt.service import (create_jwt_token, decode_jwt_token,
                             delete_refresh_tokens, retrieve_refresh_token,
                             revoked_token, store_refresh_token)
from app.services.model_service import UserService
from app.schemas.auth import LogoutResponse, TokenResponse
from settings import settings

auth_bp = Blueprint("auth", url_prefix="/auth")


@auth_bp.post("/login")
@openapi.definition(summary="User authentication", response=[TokenResponse], tag="Auth")
async def login(request):
    email = request.json.get("email")
    password = request.json.get("password")

    if not email or not password:
        return json({"error": "Email and password required"}, status=400)

    session = request.ctx.session
    async with session.begin():
        user_data = await AuthService.authenticate(
            email=email, password=SecretStr(password), session=session
        )

        if not user_data:
            return json({"error": "Invalid credentials"}, status=401)

        access_token = create_jwt_token(user_data, "access")
        refresh_token = create_jwt_token(user_data, "refresh")

        await store_refresh_token(
            user_id=user_data["user_id"], refresh_token=refresh_token, session=session
        )

        return json(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.jwt_access_token_expiration,
            }
        )


@auth_bp.post("/refresh")
@openapi.definition(
    summary="Refresh access token", response=[TokenResponse], tag="Auth"
)
async def refresh_token(request):
    refresh_token = request.json.get("refresh_token")

    if not refresh_token:
        return json({"error": "Refresh token required"}, status=400)

    session = request.ctx.session
    try:
        async with session.begin():
            payload = await decode_jwt_token(refresh_token, session)

            if payload.get("type") != "refresh":
                return json({"error": "Invalid token type"}, status=401)

            user_id = payload["sub"]
            stored_token = retrieve_refresh_token(user_id, session)

            if stored_token != refresh_token:
                return json({"error": "Invalid refresh token"}, status=401)

            user = await UserService.get_user(user_id, session)
            if not user:
                return json({"error": "User not found"}, status=404)

            user_data = {"user_id": user.id, "email": user.email, "role": user.role}

            new_access_token = create_jwt_token(user_data, "access")

            new_refresh_token = create_jwt_token(user_data, "refresh")
            await store_refresh_token(
                user_id=user_id, refresh_token=new_refresh_token, session=session
            )

            return json(
                {
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token,
                    "token_type": "bearer",
                    "expires_in": settings.jwt_refresh_token_expiration,
                }
            )

    except ExpiredSignatureError:
        return json({"error": "Refresh token expired"}, status=401)
    except InvalidTokenError as e:
        return json({"error": str(e)}, status=401)


@auth_bp.post("/logout")
@openapi.definition(summary="User logout", response=[LogoutResponse], tag="Auth")
@requires_role(Role.USER, Role.ADMIN)
async def logout(request):
    jti = request.ctx.token_jti
    expires_at = request.ctx.expires_at
    user = request.ctx.user
    token_type = request.ctx.token_type

    session = request.ctx.session

    async with session.begin():
        await revoked_token(user, token_type, jti, expires_at, session)

        await delete_refresh_tokens(request.ctx.user["id"], session)

        return json({"message": "Successfully logged out"})
