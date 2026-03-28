from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .client import BinanceFuturesClient

logger = logging.getLogger(__name__)


@dataclass
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: str
    price: str | None = None
    stop_price: str | None = None


class OrderService:
    """Application order layer built on top of Binance client."""

    def __init__(self, client: BinanceFuturesClient) -> None:
        self.client = client

    def place_order(self, order: OrderRequest, dry_run: bool = False) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "symbol": order.symbol,
            "side": order.side,
            "type": order.order_type,
            "quantity": order.quantity,
        }

        if order.order_type == "LIMIT":
            payload["timeInForce"] = "GTC"
            payload["price"] = order.price
        elif order.order_type == "STOP_MARKET":
            payload["stopPrice"] = order.stop_price

        logger.info("Order request summary | %s", payload)

        if dry_run:
            logger.info("Dry run mode enabled: Binance API call skipped")
            return {
                "symbol": order.symbol,
                "orderId": 99999999,
                "status": "FILLED" if order.order_type == "MARKET" else "NEW",
                "executedQty": "0" if order.order_type != "MARKET" else order.quantity,
                "avgPrice": order.price or "0.0",
                "type": order.order_type,
                "side": order.side,
            }

        return self.client.place_order(payload)


def format_order_response(response: dict[str, Any]) -> dict[str, Any]:
    """Extract response fields required by the assignment."""
    avg_price = response.get("avgPrice")

    if not avg_price and response.get("executedQty") and response.get("cumQuote"):
        try:
            executed_qty = float(response["executedQty"])
            cum_quote = float(response["cumQuote"])
            avg_price = f"{(cum_quote / executed_qty):.8f}" if executed_qty else "0"
        except (TypeError, ValueError, ZeroDivisionError):
            avg_price = "N/A"

    return {
        "orderId": response.get("orderId", "N/A"),
        "status": response.get("status", "N/A"),
        "executedQty": response.get("executedQty", "N/A"),
        "avgPrice": avg_price if avg_price is not None else "N/A",
    }
