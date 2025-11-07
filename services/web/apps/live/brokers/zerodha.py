import os
from typing import Dict, List

from apps.live.brokers.base import BaseBroker, OrderRequest, OrderResponse


class ZerodhaBroker(BaseBroker):
    def __init__(self):
        self.api_key = os.getenv("ZERODHA_API_KEY")
        self.api_secret = os.getenv("ZERODHA_API_SECRET")
        self.connected = False
        self.kite = None

    def connect(self) -> bool:
        try:
            return True
        except Exception as e:
            return False

    def place_order(self, order: OrderRequest) -> OrderResponse:
        if not self.connected:
            return OrderResponse("", "rejected", "Not connected to Zerodha")

        try:
            return OrderResponse("demo_order_id", "submitted", "Order placed (demo mode)")
        except Exception as e:
            return OrderResponse("", "rejected", str(e))

    def cancel_order(self, order_id: str) -> bool:
        if not self.connected:
            return False

        try:
            return True
        except Exception:
            return False

    def get_order_status(self, order_id: str) -> Dict:
        if not self.connected:
            return {}

        try:
            return {"order_id": order_id, "status": "pending"}
        except Exception:
            return {}

    def get_positions(self) -> List[Dict]:
        if not self.connected:
            return []

        try:
            return []
        except Exception:
            return []

    def get_quote(self, symbol: str, exchange: str) -> Dict:
        if not self.connected:
            return {}

        try:
            instrument_token = f"{exchange}:{symbol}"
            return {
                "symbol": symbol,
                "exchange": exchange,
                "last_price": 0.0,
                "bid": 0.0,
                "ask": 0.0,
            }
        except Exception:
            return {}

    def subscribe_quotes(self, symbols: List[str], callback) -> None:
        if not self.connected:
            return

        try:
            pass
        except Exception:
            pass

    def disconnect(self) -> None:
        if self.kite:
            self.connected = False
            self.kite = None
