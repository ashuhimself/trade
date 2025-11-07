from abc import ABC, abstractmethod
from typing import Dict


class RiskSizer(ABC):
    @abstractmethod
    def calculate_position_size(
        self,
        symbol: str,
        signal_strength: float,
        current_price: float,
        equity: float,
        current_position: float,
        volatility: float = 0.0,
    ) -> int:
        pass


class FixedRiskSizer(RiskSizer):
    def __init__(self, risk_per_trade: float = 0.02, max_position_pct: float = 0.1):
        self.risk_per_trade = risk_per_trade
        self.max_position_pct = max_position_pct

    def calculate_position_size(
        self,
        symbol: str,
        signal_strength: float,
        current_price: float,
        equity: float,
        current_position: float,
        volatility: float = 0.0,
    ) -> int:
        max_value = equity * self.max_position_pct
        quantity = int(max_value / current_price) if current_price > 0 else 0
        return int(quantity * signal_strength)


class VolatilityRiskSizer(RiskSizer):
    def __init__(self, target_volatility: float = 0.15, max_position_pct: float = 0.2):
        self.target_volatility = target_volatility
        self.max_position_pct = max_position_pct

    def calculate_position_size(
        self,
        symbol: str,
        signal_strength: float,
        current_price: float,
        equity: float,
        current_position: float,
        volatility: float = 0.0,
    ) -> int:
        if volatility <= 0 or current_price <= 0:
            return 0

        vol_scalar = self.target_volatility / volatility
        vol_scalar = min(vol_scalar, 2.0)

        max_value = equity * self.max_position_pct
        quantity = int(max_value / current_price * vol_scalar)

        return int(quantity * signal_strength)


class KellyRiskSizer(RiskSizer):
    def __init__(self, kelly_fraction: float = 0.25, max_position_pct: float = 0.15):
        self.kelly_fraction = kelly_fraction
        self.max_position_pct = max_position_pct

    def calculate_position_size(
        self,
        symbol: str,
        signal_strength: float,
        current_price: float,
        equity: float,
        current_position: float,
        volatility: float = 0.0,
    ) -> int:
        kelly_pct = self.kelly_fraction * signal_strength
        kelly_pct = min(kelly_pct, self.max_position_pct)

        value = equity * kelly_pct
        quantity = int(value / current_price) if current_price > 0 else 0

        return quantity
