from pydantic import BaseModel, ConfigDict

from .types import Decimal10_2


class TransactionsResponse(BaseModel):
    account_id: int
    amount: Decimal10_2

    model_config = ConfigDict(from_attributes=True)
