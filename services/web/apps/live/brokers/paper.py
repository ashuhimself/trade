import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from apps.data.models import Asset, Bar
from apps.live.brokers.base import BaseBroker, OrderRequest, OrderResponse


class PaperBroker(BaseBroker):
    def __init__(self):
        self.orders: Dict[str, Dict] = {}
        self.positions: Dict[str, float] = {}
        self.cash = 1000000.0
        self.connected = False
        self.quote_callbacks = []

    def connect(self) -> bool:
        self.connected = True
        return True

    def place_order(self, order: OrderRequest) -> OrderResponse:
        if not self.connected:
            return OrderResponse("", "rejected", "Not connected")

        order_id = str(uuid.uuid4())

        try:
            asset = Asset.objects.get(symbol=order.symbol, exchange__code=order.exchange)
        except Asset.DoesNotExist:
            return OrderResponse("", "rejected", f"Asset {order.symbol} not found")

        latest_bar = Bar.objects.filter(asset=asset).order_by("-timestamp").first()

        if not latest_bar:
            return OrderResponse("", "rejected", "No market data available")

        execution_price = float(latest_bar.close)

        slippage_bps = random.uniform(2, 8)
        if order.side == "buy":
            execution_price *= 1 + (slippage_bps / 10000)
        else:
            execution_price *= 1 - (slippage_bps / 10000)

        cost = execution_price * order.quantity
        commission = cost * 0.0003

        if order.side == "buy":
            required_cash = cost + commission
            if required_cash > self.cash:
                return OrderResponse("", "rejected", "Insufficient funds")

            self.cash -= required_cash
            current_pos = self.positions.get(order.symbol, 0.0)
            self.positions[order.symbol] = current_pos + order.quantity

        else:
            current_pos = self.positions.get(order.symbol, 0.0)
            if abs(current_pos) < order.quantity:
                return OrderResponse("", "rejected", "Insufficient position")

            self.cash += cost - commission
            self.positions[order.symbol] = current_pos - order.quantity

        self.orders[order_id] = {
            "order_id": order_id,
            "symbol": order.symbol,
            "exchange": order.exchange,
            "side": order.side,
            "quantity": order.quantity,
            "order_type": order.order_type,
            "price": order.price,
            "execution_price": execution_price,
            "status": "filled",
            "filled_quantity": order.quantity,
            "timestamp": datetime.now(),
        }

        return OrderResponse(order_id, "filled", "Order executed")

    def cancel_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            order = self.orders[order_id]
            if order["status"] in ["pending", "submitted"]:
                order["status"] = "cancelled"
                return True
        return False

    def get_order_status(self, order_id: str) -> Dict:
        return self.orders.get(order_id, {})

    def get_positions(self) -> List[Dict]:
        positions = []
        for symbol, quantity in self.positions.items():
            if abs(quantity) > 1e-6:
                positions.append(
                    {
                        "symbol": symbol,
                        "quantity": quantity,
                        "side": "long" if quantity > 0 else "short",
                    }
                )
        return positions

    def get_quote(self, symbol: str, exchange: str) -> Dict:
        try:
            asset = Asset.objects.get(symbol=symbol, exchange__code=exchange)
            latest_bar = Bar.objects.filter(asset=asset).order_by("-timestamp").first()

            if latest_bar:
                return {
                    "symbol": symbol,
                    "exchange": exchange,
                    "last_price": float(latest_bar.close),
                    "bid": float(latest_bar.close) * 0.9995,
                    "ask": float(latest_bar.close) * 1.0005,
                    "volume": int(latest_bar.volume),
                    "timestamp": latest_bar.timestamp,
                }
        except Asset.DoesNotExist:
            pass

        return {}

    def subscribe_quotes(self, symbols: List[str], callback) -> None:
        self.quote_callbacks.append({"symbols": symbols, "callback": callback})

    def disconnect(self) -> None:
        self.connected = False
        self.quote_callbacks.clear()
