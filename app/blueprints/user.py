from sanic import Blueprint, json
from sanic_ext import openapi
from sqlalchemy import select

from app.logger import LOGS
from app.schemas.account import AccountsResponse
from app.schemas.transaction import TransactionsResponse
from database.models.account import Account
from database.models.transaction import Transaction

user_bp = Blueprint("user", url_prefix="/user")


@user_bp.get("/accounts")
@openapi.definition(
    summary="Users accounts information", response=[AccountsResponse], tag="User"
)
async def user_accounts(request):
    user = request.ctx.user
    LOGS.debug(f"{user}")

    if not user:
        return json({"error": "User not found"}, status=404)

    session = request.ctx.session
    query = select(Account).filter_by(user_id=user["id"])
    result = await session.execute(query)
    accounts = result.scalars().all()

    validate_data = [
        AccountsResponse.model_validate(account).model_dump(mode="json")
        for account in accounts
    ]
    return json(validate_data)


@user_bp.get("/transactions")
@openapi.definition(
    summary="Users transactions information",
    response=[TransactionsResponse],
    tag="User",
)
async def user_transactions(request):
    user = request.ctx.user

    if not user:
        return json({"error": "User not found"}, status=404)

    session = request.ctx.session

    query = select(Transaction).filter_by(user_id=user["id"])
    result = await session.execute(query)
    transactions = result.scalars().all()

    validate_data = [
        TransactionsResponse.model_validate(transaction).model_dump(mode="json")
        for transaction in transactions
    ]
    return json(validate_data)
