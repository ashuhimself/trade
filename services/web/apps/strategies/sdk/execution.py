from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class ExecutionOrder:
    def __init__(
        self,
        symbol: str,
        side: str,
        quantity: int,
        order_type: str = "market",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ):
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.order_type = order_type
        self.limit_price = limit_price
        self.stop_price = stop_price


class ExecutionModel(ABC):
    @abstractmethod
    def generate_orders(
        self,
        target_positions: Dict[str, int],
        current_positions: Dict[str, float],
        current_prices: Dict[str, float],
    ) -> List[ExecutionOrder]:
        pass


class SimpleExecutionModel(ExecutionModel):
    def generate_orders(
        self,
        target_positions: Dict[str, int],
        current_positions: Dict[str, float],
        current_prices: Dict[str, float],
    ) -> List[ExecutionOrder]:
        orders = []

        all_symbols = set(target_positions.keys()) | set(current_positions.keys())

        for symbol in all_symbols:
            target = target_positions.get(symbol, 0)
            current = current_positions.get(symbol, 0.0)
            delta = target - current

            if abs(delta) < 1e-6:
                continue

            side = "buy" if delta > 0 else "sell"
            quantity = abs(int(delta))

            if quantity > 0:
                orders.append(
                    ExecutionOrder(
                        symbol=symbol,
                        side=side,
                        quantity=quantity,
                        order_type="market",
                    )
                )

        return orders
