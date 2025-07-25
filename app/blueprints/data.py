from sanic import Blueprint, json
from sanic_ext import openapi

from app.schemas.user import UserResponse

data_bp = Blueprint("user_data", url_prefix="/data")


@data_bp.get("/")
@openapi.definition(
    summary="Get current user data", response=[UserResponse], tag="User"
)
async def get_data(request):
    user_data = request.ctx.user
    if not user_data:
        return json({"error": "User not found"}, status=404)

    validate_data = UserResponse.model_validate(user_data).model_dump()
    return json(validate_data)
