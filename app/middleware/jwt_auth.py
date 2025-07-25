from datetime import datetime, timezone
from sanic.response import json

from app.jwt.service import (ExpiredSignatureError, InvalidTokenError,
                             decode_jwt_token)
from app.logger import LOGS


async def jwt_authentication(request):
    public_routes = ["login", "refresh", "docs", "openapi.json", "transaction"]

    if request.path.split("/")[-1] in public_routes:
        return

    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return json({"error": "Missing or invalid Authorization header"}, status=401)

    token = auth_header.split(" ", 1)[1]

    try:
        session = request.ctx.session

        payload = await decode_jwt_token(token, session)

        if session.in_transaction():
            await session.commit()

        LOGS.debug(f"Decoded payload: {payload}")

        if payload["type"] != "access":
            return json(
                {"error": "Invalid token type. Access token required."}, status=401
            )

        request.ctx.user = {
            "id": int(payload["sub"]),
            "full_name": payload["full_name"],
            "email": payload["email"],
            "role": payload["role"],
        }

        request.ctx.token_type = payload["type"]
        request.ctx.expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        request.ctx.token_jti = payload["jti"]

    except ExpiredSignatureError:
        return json({"error": "Token expired", "code": "token-expired"}, status=401)
    except InvalidTokenError as e:
        return json({"error": str(e)}, status=401)
    except Exception as e:
        LOGS.error(f"JWT Authentication error: {str(e)}")
        return json({"error": "Authentication failed"}, status=401)
