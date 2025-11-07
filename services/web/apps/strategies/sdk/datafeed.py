from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd


class DataFeed(ABC):
    @abstractmethod
    def get_bars(
        self,
        symbols: List[str],
        start: datetime,
        end: datetime,
        timeframe: str = "1D",
    ) -> Dict[str, pd.DataFrame]:
        pass

    @abstractmethod
    def get_latest_bar(self, symbol: str, timestamp: datetime) -> Optional[pd.Series]:
        pass

    @abstractmethod
    def get_historical_window(
        self, symbol: str, timestamp: datetime, lookback_bars: int
    ) -> pd.DataFrame:
        pass
