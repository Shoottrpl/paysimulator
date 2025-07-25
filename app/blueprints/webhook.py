from sanic import Blueprint, json
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import RequestBody
from sqlalchemy import select

from app.schemas.webhook import WebhookPayload
from app.signature.signature_service import TransactionSignatureService
from database.models.account import Account
from database.models.base import Decimal10_2
from database.models.transaction import Transaction

webhook_bp = Blueprint("webhook", url_prefix="/webhook")


@webhook_bp.post("/transaction")
@openapi.definition(
    body=RequestBody(WebhookPayload, required=True),
    summary="Create new transaction",
    tag="Transaction",
)
async def transaction_webhook(request):
    session = request.ctx.session
    body = request.json

    is_valid = TransactionSignatureService.verify_signature(body)

    if not is_valid:
        return json({"error": "Invalid signature"}, status=403)

    payload = WebhookPayload(**body)

    async with session.begin():
        existing_transaction = await session.execute(
            select(Transaction).filter_by(id=payload.transaction_id).with_for_update()
        )
        if existing_transaction.scalar():
            return json({"error": "Duplicate transaction"}, status=409)

        account = await session.get(Account, payload.account_id)
        if not account:
            account = Account(
                id=payload.account_id,
                user_id=payload.user_id,
                balance=Decimal10_2("0.00"),
            )
            session.add(account)

        transaction = Transaction(
            id=payload.transaction_id,
            user_id=payload.user_id,
            amount=payload.amount,
            account_id=payload.account_id,
            signature=payload.signature,
        )
        session.add(transaction)

        account.balance += payload.amount

        return json({"status": "success", "balance": str(account.balance)})
