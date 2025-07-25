from uuid import UUID

from pydantic import BaseModel

from .types import Decimal10_2


class WebhookPayload(BaseModel):
    transaction_id: UUID
    user_id: int
    account_id: int
    amount: Decimal10_2
    signature: str
