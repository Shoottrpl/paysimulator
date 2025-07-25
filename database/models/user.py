from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.auth.role import Role
from database.models.base import Base


class User(Base):
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[Role] = mapped_column(default=Role.USER)

    accounts: Mapped[list["Account"]] = relationship(back_populates="user")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user")
