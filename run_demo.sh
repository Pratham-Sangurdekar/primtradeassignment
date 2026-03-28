#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-/Users/pratham/Documents/binance proj/.venv/bin/python}"

cd "$SCRIPT_DIR"

echo "Running dry-run MARKET order..."
"$PYTHON_BIN" cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --order-type MARKET \
  --quantity 0.001 \
  --dry-run \
  --log-file logs/market_order.log

echo ""
echo "Running dry-run LIMIT order..."
"$PYTHON_BIN" cli.py \
  --symbol BTCUSDT \
  --side SELL \
  --order-type LIMIT \
  --quantity 0.001 \
  --price 90000 \
  --dry-run \
  --log-file logs/limit_order.log

echo ""
echo "Running dry-run STOP_MARKET order..."
"$PYTHON_BIN" cli.py \
  --symbol BTCUSDT \
  --side SELL \
  --order-type STOP_MARKET \
  --quantity 0.001 \
  --stop-price 85000 \
  --dry-run \
  --log-file logs/stop_market_order.log

echo ""
echo "Demo complete. Logs updated in ./logs"
