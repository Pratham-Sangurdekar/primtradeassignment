from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{6,20}$")


class ValidationError(ValueError):
    """Raised when user input is invalid."""


def validate_symbol(symbol: str) -> str:
    cleaned = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(cleaned):
        raise ValidationError("Invalid symbol format. Example: BTCUSDT")
    return cleaned


def validate_side(side: str) -> str:
    cleaned = side.strip().upper()
    if cleaned not in {"BUY", "SELL"}:
        raise ValidationError("Side must be BUY or SELL")
    return cleaned


def validate_order_type(order_type: str) -> str:
    cleaned = order_type.strip().upper()
    if cleaned not in {"MARKET", "LIMIT", "STOP_MARKET"}:
        raise ValidationError("Order type must be MARKET, LIMIT, or STOP_MARKET")
    return cleaned


def validate_positive_decimal(value: str, field_name: str) -> str:
    try:
        parsed = Decimal(value)
    except (InvalidOperation, TypeError) as exc:
        raise ValidationError(f"{field_name} must be a valid number") from exc

    if parsed <= 0:
        raise ValidationError(f"{field_name} must be greater than 0")

    return format(parsed.normalize(), "f")
