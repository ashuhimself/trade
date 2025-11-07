from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd


class SignalResult:
    def __init__(
        self,
        symbol: str,
        signal: int,
        strength: float = 1.0,
        metadata: Optional[Dict] = None,
    ):
        self.symbol = symbol
        self.signal = signal
        self.strength = strength
        self.metadata = metadata or {}

    def __repr__(self):
        return f"SignalResult({self.symbol}, signal={self.signal}, strength={self.strength})"


class Signal(ABC):
    @abstractmethod
    def generate(
        self,
        timestamp: datetime,
        bars: Dict[str, pd.DataFrame],
        current_positions: Dict[str, float],
    ) -> List[SignalResult]:
        pass

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        return df
