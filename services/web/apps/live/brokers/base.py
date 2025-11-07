from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class OrderRequest:
    def __init__(
        self,
        symbol: str,
        exchange: str,
        side: str,
        quantity: int,
        order_type: str = "market",
        price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        product: str = "MIS",
    ):
        self.symbol = symbol
        self.exchange = exchange
        self.side = side
        self.quantity = quantity
        self.order_type = order_type
        self.price = price
        self.trigger_price = trigger_price
        self.product = product


class OrderResponse:
    def __init__(
        self,
        order_id: str,
        status: str,
        message: str = "",
    ):
        self.order_id = order_id
        self.status = status
        self.message = message


class BaseBroker(ABC):
    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def place_order(self, order: OrderRequest) -> OrderResponse:
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        pass

    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict:
        pass

    @abstractmethod
    def get_positions(self) -> List[Dict]:
        pass

    @abstractmethod
    def get_quote(self, symbol: str, exchange: str) -> Dict:
        pass

    @abstractmethod
    def subscribe_quotes(self, symbols: List[str], callback) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass
