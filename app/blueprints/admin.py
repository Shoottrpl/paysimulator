from sanic import Blueprint, json
from sanic_ext import openapi, validate
from sanic_ext.extensions.openapi.definitions import RequestBody
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth.decorators import requires_role
from app.auth.role import Role
from app.auth.schema import UserCreate
from app.auth.service import AuthService
from app.services.model_service import UserService
from app.schemas.account import UserWithAccountsResponse
from app.schemas.user import UserUpdate
from database.models.user import User

admin_bp = Blueprint("admin", url_prefix="/admin")


@admin_bp.post("/create")
@openapi.definition(
    body=RequestBody(UserCreate, required=True), summary="Create new user", tag="Admin"
)
@validate(json=UserCreate)
@requires_role(Role.ADMIN)
async def user_create(request, body):
    session = request.ctx.session
    async with session.begin():
        query = select(User).filter_by(email=body.email)
        result = await session.execute(query)
        user = result.scalar()
        if user:
            return json({"user": "exist"})
        new_user = User(
            full_name=body.full_name,
            email=body.email,
            password_hash=AuthService.hash_password(body.password),
            role=body.role,
        )
        session.add(new_user)

    return json({"user": "successful create"})


@admin_bp.delete("/delete/<user_id:int>")
@openapi.definition(summary="Delete user", tag="Admin")
@requires_role(Role.ADMIN)
async def user_delete(request, user_id: int):
    session = request.ctx.session
    async with session.begin():
        user = await UserService.get_user(user_id, session)
        if not user:
            return json({"user": "not exist"})

        await session.delete(user)

    return json({"user": "deleted"})


@admin_bp.put("/update/<user_id:int>")
@openapi.definition(
    body=RequestBody(UserUpdate, required=True), summary="Update user", tag="Admin"
)
@validate(json=UserUpdate)
@requires_role(Role.ADMIN)
async def user_update(request, body: UserUpdate, user_id: int):
    session = request.ctx.session
    async with session.begin():
        user = await UserService.get_user(user_id, session)
        if not user:
            return json({"user": "not exist"})

        update_data = body.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(user, key, value)

    return json({"user": "updated"})


@admin_bp.get("/users-accounts")
@openapi.definition(
    summary="Users accounts information",
    response=[UserWithAccountsResponse],
    tag="Admin",
)
@requires_role(Role.ADMIN)
async def users_accounts(request):
    session = request.ctx.session

    result = await session.execute(
        select(User).options(selectinload(User.accounts)).order_by(User.id)
    )

    users = result.scalars().all()

    validate_data = [
        UserWithAccountsResponse.model_validate(user).model_dump(mode="json")
        for user in users
    ]

    return json(validate_data)
