from datetime import datetime
from typing import Dict, List

import numpy as np
import pandas as pd

from apps.strategies.sdk import Signal, SignalResult


class MomentumBreakoutSignal(Signal):
    def __init__(
        self,
        fast_period: int = 15,
        slow_period: int = 30,
        volume_sma_period: int = 20,
        volume_multiplier: float = 2.0,
        atr_period: int = 14,
        atr_multiplier: float = 1.5,
    ):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.volume_sma_period = volume_sma_period
        self.volume_multiplier = volume_multiplier
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier

    def generate(
        self,
        timestamp: datetime,
        bars: Dict[str, pd.DataFrame],
        current_positions: Dict[str, float],
    ) -> List[SignalResult]:
        signals = []

        for symbol, df in bars.items():
            if len(df) < max(self.slow_period, self.volume_sma_period, self.atr_period):
                continue

            df = df.copy()

            df["fast_ma"] = df["close"].rolling(self.fast_period).mean()
            df["slow_ma"] = df["close"].rolling(self.slow_period).mean()
            df["volume_sma"] = df["volume"].rolling(self.volume_sma_period).mean()

            high_low = df["high"] - df["low"]
            high_close = abs(df["high"] - df["close"].shift())
            low_close = abs(df["low"] - df["close"].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df["atr"] = true_range.rolling(self.atr_period).mean()

            last_row = df.iloc[-1]
            prev_row = df.iloc[-2]

            fast_ma = last_row["fast_ma"]
            slow_ma = last_row["slow_ma"]
            prev_fast_ma = prev_row["fast_ma"]
            prev_slow_ma = prev_row["slow_ma"]

            volume = last_row["volume"]
            volume_sma = last_row["volume_sma"]
            price = last_row["close"]
            atr_val = last_row["atr"]

            high = last_row["high"]
            low = last_row["low"]

            current_pos = current_positions.get(symbol, 0.0)

            signal = 0
            strength = 1.0

            volume_surge = volume > volume_sma * self.volume_multiplier

            breakout_up = high > prev_row["high"] + self.atr_multiplier * atr_val
            breakout_down = low < prev_row["low"] - self.atr_multiplier * atr_val

            if current_pos == 0:
                if (
                    fast_ma > slow_ma
                    and prev_fast_ma <= prev_slow_ma
                    and volume_surge
                    and breakout_up
                ):
                    signal = 1
                    strength = 1.0

                elif (
                    fast_ma < slow_ma
                    and prev_fast_ma >= prev_slow_ma
                    and volume_surge
                    and breakout_down
                ):
                    signal = -1
                    strength = 1.0

            elif current_pos > 0:
                if fast_ma < slow_ma:
                    signal = -1
                    strength = 1.0

            elif current_pos < 0:
                if fast_ma > slow_ma:
                    signal = 1
                    strength = 1.0

            if signal != 0:
                signals.append(
                    SignalResult(
                        symbol=symbol,
                        signal=signal,
                        strength=strength,
                        metadata={
                            "fast_ma": float(fast_ma),
                            "slow_ma": float(slow_ma),
                            "volume": float(volume),
                            "atr": float(atr_val),
                        },
                    )
                )

        return signals


class MomentumBreakoutStrategy:
    name = "Momentum Breakout"
    description = "15/30 minute momentum breakout with volume filter for NSE FNO"

    @staticmethod
    def get_default_parameters():
        return {
            "fast_period": 15,
            "slow_period": 30,
            "volume_sma_period": 20,
            "volume_multiplier": 2.0,
            "atr_period": 14,
            "atr_multiplier": 1.5,
            "max_position_pct": 0.15,
        }
