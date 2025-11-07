"""
Momentum Breakout Strategy using Polars (10-100x faster than pandas)
"""
from datetime import datetime
from typing import Dict, List

import numpy as np
import polars as pl

from apps.strategies.sdk import Signal, SignalResult


class MomentumBreakoutPolarsSignal(Signal):
    """High-performance momentum strategy using Polars"""

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
        bars: Dict[str, pl.DataFrame],  # Polars DataFrame instead of pandas
        current_positions: Dict[str, float],
    ) -> List[SignalResult]:
        signals = []

        for symbol, df in bars.items():
            if len(df) < max(self.slow_period, self.volume_sma_period, self.atr_period):
                continue

            # Polars is much faster for these operations
            df = df.with_columns(
                [
                    # Moving averages
                    pl.col("close")
                    .rolling_mean(window_size=self.fast_period)
                    .alias("fast_ma"),
                    pl.col("close")
                    .rolling_mean(window_size=self.slow_period)
                    .alias("slow_ma"),
                    pl.col("volume")
                    .rolling_mean(window_size=self.volume_sma_period)
                    .alias("volume_sma"),
                ]
            )

            # Calculate ATR using Polars expressions (vectorized)
            df = df.with_columns(
                [
                    (pl.col("high") - pl.col("low")).alias("high_low"),
                    (pl.col("high") - pl.col("close").shift(1)).abs().alias("high_close"),
                    (pl.col("low") - pl.col("close").shift(1)).abs().alias("low_close"),
                ]
            )

            df = df.with_columns(
                [
                    pl.max_horizontal(["high_low", "high_close", "low_close"])
                    .rolling_mean(window_size=self.atr_period)
                    .alias("atr")
                ]
            )

            # Get last two rows
            last_row = df.row(-1, named=True)
            prev_row = df.row(-2, named=True)

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


class MomentumBreakoutPolarsStrategy:
    """Polars-based strategy - significantly faster than pandas"""

    name = "Momentum Breakout (Polars)"
    description = "High-performance 15/30 momentum breakout using Polars library"

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


# Utility function to convert pandas DataFrame to Polars
def pandas_to_polars(df):
    """Convert pandas DataFrame to Polars for faster processing"""
    return pl.from_pandas(df)


# Utility function to convert Polars DataFrame to pandas (if needed for compatibility)
def polars_to_pandas(df):
    """Convert Polars DataFrame back to pandas if needed"""
    return df.to_pandas()
