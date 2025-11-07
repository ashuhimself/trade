from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd


class BaseStrategy(ABC):
    def __init__(
        self,
        name: str,
        universe: List[str],
        parameters: Dict[str, Any],
        datafeed: "DataFeed",
        signal: "Signal",
        risk_sizer: "RiskSizer",
        execution_model: "ExecutionModel",
    ):
        self.name = name
        self.universe = universe
        self.parameters = parameters
        self.datafeed = datafeed
        self.signal = signal
        self.risk_sizer = risk_sizer
        self.execution_model = execution_model
        self.positions: Dict[str, float] = {}
        self.cash = parameters.get("initial_capital", 1000000.0)
        self.equity = self.cash
        self.metadata: Dict[str, Any] = {}

    @abstractmethod
    def on_bar(self, timestamp: datetime, bars: Dict[str, pd.Series]) -> None:
        pass

    @abstractmethod
    def on_order_fill(self, symbol: str, side: str, quantity: int, price: float) -> None:
        pass

    def get_position(self, symbol: str) -> float:
        return self.positions.get(symbol, 0.0)

    def update_equity(self, current_prices: Dict[str, float]) -> None:
        positions_value = sum(
            qty * current_prices.get(symbol, 0.0) for symbol, qty in self.positions.items()
        )
        self.equity = self.cash + positions_value
