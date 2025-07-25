from pydantic import BaseModel, ConfigDict

from .types import Decimal10_2


class AccountsResponse(BaseModel):
    id: int
    balance: Decimal10_2

    model_config = ConfigDict(from_attributes=True)


class UserWithAccountsResponse(BaseModel):
    id: int
    full_name: str
    accounts: list[AccountsResponse] = []

    model_config = ConfigDict(from_attributes=True)
