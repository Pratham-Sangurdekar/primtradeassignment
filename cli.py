from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceAPIError, BinanceFuturesClient
from bot.logging_config import setup_logging
from bot.orders import OrderRequest, OrderService, format_order_response
from bot.validators import (
    ValidationError,
    validate_order_type,
    validate_positive_decimal,
    validate_side,
    validate_symbol,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place Binance Futures Testnet (USDT-M) MARKET/LIMIT/STOP_MARKET orders via CLI."
    )
    parser.add_argument("--symbol", required=True, help="Trading symbol, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--order-type", required=True, help="MARKET, LIMIT, or STOP_MARKET")
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", help="Price (required for LIMIT)")
    parser.add_argument(
        "--stop-price",
        help="Stop trigger price (required for STOP_MARKET)",
    )
    parser.add_argument(
        "--base-url",
        default="https://testnet.binancefuture.com",
        help="Binance Futures base URL",
    )
    parser.add_argument(
        "--log-file",
        default="logs/trading_bot.log",
        help="Path to log file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate + print order flow without calling Binance API",
    )
    return parser


def validate_cli_args(args: argparse.Namespace) -> OrderRequest:
    symbol = validate_symbol(args.symbol)
    side = validate_side(args.side)
    order_type = validate_order_type(args.order_type)
    quantity = validate_positive_decimal(args.quantity, "quantity")

    price: str | None = None
    if order_type == "LIMIT":
        if args.price is None:
            raise ValidationError("price is required when order type is LIMIT")
        if args.stop_price is not None:
            raise ValidationError("stop-price must not be provided for LIMIT orders")
        price = validate_positive_decimal(args.price, "price")

    stop_price: str | None = None
    if order_type == "STOP_MARKET":
        if args.stop_price is None:
            raise ValidationError("stop-price is required when order type is STOP_MARKET")
        if args.price is not None:
            raise ValidationError("price must not be provided for STOP_MARKET orders")
        stop_price = validate_positive_decimal(args.stop_price, "stop-price")

    if order_type == "MARKET":
        if args.price is not None:
            raise ValidationError("price must not be provided for MARKET orders")
        if args.stop_price is not None:
            raise ValidationError("stop-price must not be provided for MARKET orders")

    return OrderRequest(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
    )


def get_client(base_url: str, dry_run: bool) -> BinanceFuturesClient:
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not dry_run and (not api_key or not api_secret):
        raise ValidationError(
            "BINANCE_API_KEY and BINANCE_API_SECRET must be set in env/.env for real orders"
        )

    return BinanceFuturesClient(
        api_key=api_key or "dry_run_key",
        api_secret=api_secret or "dry_run_secret",
        base_url=base_url,
    )


def print_order_summary(order: OrderRequest) -> None:
    print("\nOrder Request Summary")
    print("---------------------")
    print(f"Symbol      : {order.symbol}")
    print(f"Side        : {order.side}")
    print(f"Order Type  : {order.order_type}")
    print(f"Quantity    : {order.quantity}")
    if order.price is not None:
        print(f"Price       : {order.price}")
    if order.stop_price is not None:
        print(f"Stop Price  : {order.stop_price}")


def print_order_response(response: dict[str, str]) -> None:
    print("\nOrder Response")
    print("--------------")
    print(f"Order ID     : {response['orderId']}")
    print(f"Status       : {response['status']}")
    print(f"Executed Qty : {response['executedQty']}")
    print(f"Avg Price    : {response['avgPrice']}")


def main() -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    setup_logging(args.log_file)

    try:
        order_request = validate_cli_args(args)
        print_order_summary(order_request)

        client = get_client(args.base_url, args.dry_run)
        service = OrderService(client)
        raw_response = service.place_order(order_request, dry_run=args.dry_run)
        response = format_order_response(raw_response)
        print_order_response(response)

        print("\n✅ Success: order processed.")
        return 0

    except ValidationError as exc:
        print(f"\n❌ Input validation error: {exc}")
        return 2
    except BinanceAPIError as exc:
        print(f"\n❌ Binance API error: {exc}")
        return 3
    except Exception as exc:  # noqa: BLE001
        print(f"\n❌ Unexpected error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
