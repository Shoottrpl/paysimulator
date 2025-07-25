from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.account import Account
from database.models.user import User


class UserService:
    @staticmethod
    async def create_user(user_data: int, session: AsyncSession) -> User:
        new_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            password_hash=user_data.password_hash,
            role=user_data.role,
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    @staticmethod
    async def get_user(user_id: int, session: AsyncSession) -> User:
        user = await session.get(User, user_id)
        return user

    @staticmethod
    async def get_by_email(email: str, session: AsyncSession):
        user = await session.execute(select(User).where(User.email == email))
        return user.scalar_one_or_none()

    @staticmethod
    async def get_user_accounts(user_id: int, session: AsyncSession):
        accounts = await session.scalars(
            select(Account).where(Account.user_id == user_id)
        )

        return [
            {
                "account_id": account.id,
                "account_balance": account.balance,
            }
            for account in accounts
        ]
