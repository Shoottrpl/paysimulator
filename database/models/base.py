from datetime import datetime
from typing import Tuple

from sqlalchemy import DateTime, Integer, Numeric, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (DeclarativeBase, Mapped, declared_attr,
                            mapped_column)

from app.schemas.types import Decimal10_2


class Base(AsyncAttrs, DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy

    """

    __abstract__ = True

    type_annotation_map = {Decimal10_2: Numeric(10, 2)}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

    repr_cols_num: int = 3
    repr_cols: Tuple[str, ...] = tuple()

    def __repr__(self) -> str:
        """
        Возвращает строковое представление объектов.

        Имя класса и значения колонок, по умолчанию отображает первые 'repr_cols_num' колонок.
        :return: Строковое представление объекта
        """
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {','.join(cols)}>"
