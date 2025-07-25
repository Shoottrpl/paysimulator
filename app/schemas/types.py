from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, WithJsonSchema


def convert_to_decimal(v) -> Decimal:
    if isinstance(v, Decimal):
        return v.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)
    return Decimal(v).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)


def validate_decimal(v: Decimal) -> Decimal:
    exponent = int(v.as_tuple().exponent)
    if abs(exponent) != 2:
        raise ValueError("Должно быть 2 символа после запятой")
    return v


Decimal10_2 = Annotated[
    Decimal,
    BeforeValidator(convert_to_decimal),
    AfterValidator(validate_decimal),
    WithJsonSchema(
        {
            "type": "string",
            "format": "decimal",
            "pattern": r"^-?\d+\.\d{2}$",
            "examples": ["100.00", "-50.25"],
        },
        mode="serialization",
    ),
]
