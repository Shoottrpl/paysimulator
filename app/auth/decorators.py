from functools import wraps
from typing import Callable

from sanic import json

from .role import Role


def requires_role(*required_roles: Role):
    def decorator(f: Callable):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            if not hasattr(request.ctx, "user"):
                error = getattr(request.ctx, "auth_error", "Unauthorized")
                return json({"error": error}, status=401)

            user_role = request.ctx.user.get("role", "")
            if not user_role or Role(user_role) not in required_roles:
                return json({"error": "Insufficient permissions"}, status=403)

            return await f(request, *args, **kwargs)

        return decorated_function

    return decorator
