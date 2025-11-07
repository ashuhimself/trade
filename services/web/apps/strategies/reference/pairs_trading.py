from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint

from apps.strategies.sdk import Signal, SignalResult


class PairsTradingSignal(Signal):
    def __init__(
        self,
        lookback_periods: int = 60,
        entry_z_score: float = 2.0,
        exit_z_score: float = 0.5,
        cointegration_pvalue: float = 0.05,
    ):
        self.lookback_periods = lookback_periods
        self.entry_z_score = entry_z_score
        self.exit_z_score = exit_z_score
        self.cointegration_pvalue = cointegration_pvalue
        self.pairs_cache = {}

    def generate(
        self,
        timestamp: datetime,
        bars: Dict[str, pd.DataFrame],
        current_positions: Dict[str, float],
    ) -> List[SignalResult]:
        signals = []

        symbols = list(bars.keys())
        if len(symbols) < 2:
            return signals

        pairs = self._find_cointegrated_pairs(bars)

        for pair in pairs:
            symbol1, symbol2 = pair

            df1 = bars[symbol1].tail(self.lookback_periods)
            df2 = bars[symbol2].tail(self.lookback_periods)

            if len(df1) < self.lookback_periods or len(df2) < self.lookback_periods:
                continue

            price1 = df1["close"].values
            price2 = df2["close"].values

            hedge_ratio = self._calculate_hedge_ratio(price1, price2)
            spread = price1 - hedge_ratio * price2

            spread_mean = np.mean(spread)
            spread_std = np.std(spread)

            if spread_std == 0:
                continue

            z_score = (spread[-1] - spread_mean) / spread_std

            pos1 = current_positions.get(symbol1, 0.0)
            pos2 = current_positions.get(symbol2, 0.0)

            in_position = abs(pos1) > 0 or abs(pos2) > 0

            if not in_position:
                if z_score > self.entry_z_score:
                    signals.append(
                        SignalResult(
                            symbol=symbol1,
                            signal=-1,
                            strength=min(abs(z_score) / self.entry_z_score, 1.0),
                            metadata={"z_score": float(z_score), "pair": symbol2},
                        )
                    )
                    signals.append(
                        SignalResult(
                            symbol=symbol2,
                            signal=1,
                            strength=min(abs(z_score) / self.entry_z_score, 1.0),
                            metadata={"z_score": float(z_score), "pair": symbol1},
                        )
                    )

                elif z_score < -self.entry_z_score:
                    signals.append(
                        SignalResult(
                            symbol=symbol1,
                            signal=1,
                            strength=min(abs(z_score) / self.entry_z_score, 1.0),
                            metadata={"z_score": float(z_score), "pair": symbol2},
                        )
                    )
                    signals.append(
                        SignalResult(
                            symbol=symbol2,
                            signal=-1,
                            strength=min(abs(z_score) / self.entry_z_score, 1.0),
                            metadata={"z_score": float(z_score), "pair": symbol1},
                        )
                    )

            else:
                if abs(z_score) < self.exit_z_score:
                    if pos1 != 0:
                        signals.append(
                            SignalResult(
                                symbol=symbol1,
                                signal=-np.sign(pos1),
                                strength=1.0,
                                metadata={"z_score": float(z_score), "exit": True},
                            )
                        )
                    if pos2 != 0:
                        signals.append(
                            SignalResult(
                                symbol=symbol2,
                                signal=-np.sign(pos2),
                                strength=1.0,
                                metadata={"z_score": float(z_score), "exit": True},
                            )
                        )

        return signals

    def _find_cointegrated_pairs(self, bars: Dict[str, pd.DataFrame]) -> List[Tuple[str, str]]:
        symbols = list(bars.keys())
        pairs = []

        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                symbol1 = symbols[i]
                symbol2 = symbols[j]

                df1 = bars[symbol1].tail(self.lookback_periods)
                df2 = bars[symbol2].tail(self.lookback_periods)

                if len(df1) < self.lookback_periods or len(df2) < self.lookback_periods:
                    continue

                price1 = df1["close"].values
                price2 = df2["close"].values

                try:
                    _, pvalue, _ = coint(price1, price2)

                    if pvalue < self.cointegration_pvalue:
                        pairs.append((symbol1, symbol2))
                except Exception:
                    continue

        return pairs

    def _calculate_hedge_ratio(self, price1: np.ndarray, price2: np.ndarray) -> float:
        return np.polyfit(price2, price1, 1)[0]


class PairsTradingStrategy:
    name = "Pairs Trading"
    description = "Statistical arbitrage via cointegration on sector heavyweights"

    @staticmethod
    def get_default_parameters():
        return {
            "lookback_periods": 60,
            "entry_z_score": 2.0,
            "exit_z_score": 0.5,
            "cointegration_pvalue": 0.05,
            "max_position_pct": 0.1,
        }
