from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)


class BinanceAPIError(Exception):
    """Raised when Binance returns a non-success response."""

    def __init__(self, status_code: int, response_text: str) -> None:
        super().__init__(f"Binance API error {status_code}: {response_text}")
        self.status_code = status_code
        self.response_text = response_text


class BinanceFuturesClient:
    """Minimal Binance USDT-M Futures Testnet client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://testnet.binancefuture.com",
        timeout_seconds: int = 15,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()

    def _sign(self, params: dict[str, Any]) -> str:
        query_string = urlencode(params, doseq=True)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        payload = dict(params or {})
        headers = {"X-MBX-APIKEY": self.api_key}

        if signed:
            payload["timestamp"] = int(time.time() * 1000)
            payload.setdefault("recvWindow", 5000)
            payload["signature"] = self._sign(payload)

        logger.info("API request | method=%s url=%s params=%s", method, url, payload)

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=payload,
                headers=headers,
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:
            logger.exception("Network error while calling Binance API")
            raise

        logger.info(
            "API response | status=%s body=%s",
            response.status_code,
            response.text,
        )

        if response.status_code >= 400:
            raise BinanceAPIError(response.status_code, response.text)

        return response.json()

    def place_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Place a futures order on USDT-M Testnet."""
        return self._request("POST", "/fapi/v1/order", params=payload, signed=True)
