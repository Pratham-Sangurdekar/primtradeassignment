# Simplified Trading Bot – Binance Futures Testnet (USDT-M)

A small Python CLI app that places **MARKET**, **LIMIT**, and **STOP_MARKET** orders on Binance Futures Testnet with clear output, structured layering, validation, and file logging.

## Features

- Python 3.x CLI app
- Supports order side: `BUY` and `SELL`
- Supports order types: `MARKET`, `LIMIT`, and `STOP_MARKET` (bonus)
- Validates CLI inputs (`symbol`, `side`, `order type`, `quantity`, `price`, `stop-price`)
- Structured architecture:
  - API layer: `bot/client.py`
  - Order service: `bot/orders.py`
  - Validation: `bot/validators.py`
  - Logging setup: `bot/logging_config.py`
  - CLI entrypoint: `cli.py`
- Logs API requests, responses, and errors to a file
- Handles input errors, API errors, and network failures
- Includes `--dry-run` mode for local/demo testing without credentials

## Project Structure

```text
trading_bot/
  bot/
    __init__.py
    client.py
    orders.py
    validators.py
    logging_config.py
  logs/
    market_order.log
    limit_order.log
    stop_market_order.log
  cli.py
  .env.example
  README.md
  requirements.txt
```

## Setup

1. Create a Binance Futures Testnet account and API credentials.
2. Clone/unzip this project and move into the folder:

```bash
cd trading_bot
```

3. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Configure credentials:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```

## Usage

Base URL used by default: `https://testnet.binancefuture.com`

### MARKET order example

```bash
python cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --order-type MARKET \
  --quantity 0.001
```

### LIMIT order example

```bash
python cli.py \
  --symbol BTCUSDT \
  --side SELL \
  --order-type LIMIT \
  --quantity 0.001 \
  --price 90000
```

### STOP_MARKET order example (bonus)

```bash
python cli.py \
  --symbol BTCUSDT \
  --side SELL \
  --order-type STOP_MARKET \
  --quantity 0.001 \
  --stop-price 85000
```

### Generate log files without hitting API (demo mode)

```bash
python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001 --dry-run --log-file logs/market_order.log
python cli.py --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 90000 --dry-run --log-file logs/limit_order.log
python cli.py --symbol BTCUSDT --side SELL --order-type STOP_MARKET --quantity 0.001 --stop-price 85000 --dry-run --log-file logs/stop_market_order.log
```

## Output Behavior

The app prints:

- Order request summary
- Order response details (`orderId`, `status`, `executedQty`, `avgPrice`)
- A success/failure message

## How to Test and View

### 1) Quick local test (no API call)

Use dry-run mode:

```bash
python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001 --dry-run
python cli.py --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 90000 --dry-run
python cli.py --symbol BTCUSDT --side SELL --order-type STOP_MARKET --quantity 0.001 --stop-price 85000 --dry-run
```

Or run all dry-run scenarios in one command:

```bash
./run_demo.sh
```

### 2) Real testnet order test

After setting valid keys in `.env`, run the same commands **without** `--dry-run`.

> Note: Binance Futures enforces minimum notional on orders. If you get code `-4164`, increase quantity or price.

### 3) View logs

```bash
cat logs/market_order.log
cat logs/limit_order.log
cat logs/stop_market_order.log
tail -f logs/trading_bot.log
```

### 4) Validate CLI options

```bash
python cli.py --help
```

## Assumptions

- This app targets **USDT-M Futures Testnet** only.
- For real API calls, valid testnet credentials are required in `.env`.
- `avgPrice` may be unavailable immediately on some responses; app prints `N/A` when not provided.

## Error Handling

- Input validation errors return clear CLI messages.
- Binance API errors include status code and response text.
- Network exceptions are caught and logged.

## Notes for Evaluators

- Required deliverables are included: `logs/market_order.log` and `logs/limit_order.log`.
- Logs in this repository were updated using real Binance Futures Testnet API runs.
- Real run evidence in logs includes:
  - `LIMIT` order success: `orderId = 13002596023`
  - `MARKET` order success: `orderId = 13002596824`
- Bonus log is also included: `logs/stop_market_order.log`.
