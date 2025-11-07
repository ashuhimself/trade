from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from apps.strategies.sdk import Signal, SignalResult


class MeanReversionVWAPSignal(Signal):
    def __init__(
        self,
        lookback_periods: int = 20,
        entry_std: float = 2.0,
        exit_std: float = 0.5,
        volume_filter_multiplier: float = 1.5,
    ):
        self.lookback_periods = lookback_periods
        self.entry_std = entry_std
        self.exit_std = exit_std
        self.volume_filter_multiplier = volume_filter_multiplier

    def generate(
        self,
        timestamp: datetime,
        bars: Dict[str, pd.DataFrame],
        current_positions: Dict[str, float],
    ) -> List[SignalResult]:
        signals = []

        for symbol, df in bars.items():
            if len(df) < self.lookback_periods:
                continue

            df = df.copy().tail(self.lookback_periods)

            df["vwap"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()

            df["price_std"] = df["close"].rolling(self.lookback_periods).std()

            df["upper_band"] = df["vwap"] + self.entry_std * df["price_std"]
            df["lower_band"] = df["vwap"] - self.entry_std * df["price_std"]

            df["exit_upper"] = df["vwap"] + self.exit_std * df["price_std"]
            df["exit_lower"] = df["vwap"] - self.exit_std * df["price_std"]

            avg_volume = df["volume"].rolling(self.lookback_periods).mean()
            current_volume = df["volume"].iloc[-1]

            last_price = df["close"].iloc[-1]
            vwap = df["vwap"].iloc[-1]
            lower_band = df["lower_band"].iloc[-1]
            upper_band = df["upper_band"].iloc[-1]
            exit_lower = df["exit_lower"].iloc[-1]
            exit_upper = df["exit_upper"].iloc[-1]

            current_pos = current_positions.get(symbol, 0.0)

            signal = 0
            strength = 1.0

            if current_volume > avg_volume.iloc[-1] * self.volume_filter_multiplier:
                if current_pos == 0:
                    if last_price < lower_band:
                        signal = 1
                        strength = abs(last_price - vwap) / df["price_std"].iloc[-1]

                    elif last_price > upper_band:
                        signal = -1
                        strength = abs(last_price - vwap) / df["price_std"].iloc[-1]

                elif current_pos > 0:
                    if last_price >= exit_lower:
                        signal = -1
                        strength = 1.0

                elif current_pos < 0:
                    if last_price <= exit_upper:
                        signal = 1
                        strength = 1.0

            if signal != 0:
                signals.append(
                    SignalResult(
                        symbol=symbol,
                        signal=signal,
                        strength=min(strength, 1.0),
                        metadata={
                            "vwap": float(vwap),
                            "price": float(last_price),
                            "volume": float(current_volume),
                        },
                    )
                )

        return signals


class MeanReversionVWAPStrategy:
    name = "Mean Reversion to VWAP"
    description = "Intraday mean reversion to VWAP on liquid Indian equities"

    @staticmethod
    def get_default_parameters():
        return {
            "lookback_periods": 20,
            "entry_std": 2.0,
            "exit_std": 0.5,
            "volume_filter_multiplier": 1.5,
            "risk_per_trade": 0.02,
            "max_position_pct": 0.1,
        }
