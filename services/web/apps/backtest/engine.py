from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from django.utils import timezone

from apps.backtest.models import BacktestMetrics, EquityCurve, WeeklyReturn
from apps.data.models import Asset, Bar
from apps.live.models import Order, Trade
from apps.strategies.models import StrategyRun
from apps.strategies.sdk import FeeModel, SlippageModel


class BacktestEngine:
    def __init__(
        self,
        strategy_run: StrategyRun,
        initial_capital: float,
        slippage_model: SlippageModel,
        fee_model: FeeModel,
    ):
        self.strategy_run = strategy_run
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.equity = initial_capital
        self.positions: Dict[int, float] = {}
        self.slippage_model = slippage_model
        self.fee_model = fee_model

        self.equity_curve_data = []
        self.trades_data = []
        self.orders_data = []

        self.peak_equity = initial_capital
        self.current_drawdown = 0.0

    def run(
        self,
        universe: List[Asset],
        start_date: datetime,
        end_date: datetime,
        on_bar_callback,
    ):
        bars_qs = Bar.objects.filter(
            asset__in=universe,
            timestamp__gte=start_date,
            timestamp__lte=end_date,
        ).order_by("timestamp", "asset")

        bars_df = pd.DataFrame(bars_qs.values())
        if bars_df.empty:
            return

        bars_by_timestamp = bars_df.groupby("timestamp")

        for timestamp, group in bars_by_timestamp:
            bars_dict = {}
            for _, row in group.iterrows():
                asset_id = row["asset_id"]
                bars_dict[asset_id] = row

            current_prices = {aid: float(row["close"]) for aid, row in bars_dict.items()}

            signals = on_bar_callback(timestamp, bars_dict, self.positions)

            self._process_signals(signals, current_prices, timestamp)

            self._update_equity(current_prices, timestamp)

        self._finalize()

    def _process_signals(self, signals: List[Dict], current_prices: Dict[int, float], timestamp):
        for signal in signals:
            asset_id = signal["asset_id"]
            target_quantity = signal["quantity"]
            current_quantity = self.positions.get(asset_id, 0.0)

            delta = target_quantity - current_quantity

            if abs(delta) < 1e-6:
                continue

            side = "buy" if delta > 0 else "sell"
            quantity = abs(int(delta))
            price = current_prices.get(asset_id, 0.0)

            if price <= 0:
                continue

            execution_price = self.slippage_model.apply(price, quantity, side)
            commission = self.fee_model.calculate(execution_price, quantity, side)

            cost = execution_price * quantity
            if side == "buy":
                required_cash = cost + commission
                if required_cash > self.cash:
                    continue
                self.cash -= required_cash
                self.positions[asset_id] = self.positions.get(asset_id, 0.0) + quantity
            else:
                self.cash += cost - commission
                self.positions[asset_id] = self.positions.get(asset_id, 0.0) - quantity

            self.orders_data.append(
                {
                    "asset_id": asset_id,
                    "side": side,
                    "quantity": quantity,
                    "price": price,
                    "execution_price": execution_price,
                    "commission": commission,
                    "timestamp": timestamp,
                }
            )

    def _update_equity(self, current_prices: Dict[int, float], timestamp):
        positions_value = sum(
            qty * current_prices.get(aid, 0.0) for aid, qty in self.positions.items()
        )
        self.equity = self.cash + positions_value

        if self.equity > self.peak_equity:
            self.peak_equity = self.equity

        self.current_drawdown = (self.peak_equity - self.equity) / self.peak_equity

        self.equity_curve_data.append(
            {
                "timestamp": timestamp,
                "equity": self.equity,
                "cash": self.cash,
                "positions_value": positions_value,
                "drawdown": self.current_drawdown,
            }
        )

    def _finalize(self):
        if not self.equity_curve_data:
            return

        equity_df = pd.DataFrame(self.equity_curve_data)
        equity_df["daily_return"] = equity_df["equity"].pct_change()

        for _, row in equity_df.iterrows():
            EquityCurve.objects.create(
                strategy_run=self.strategy_run,
                timestamp=row["timestamp"],
                equity=row["equity"],
                cash=row["cash"],
                positions_value=row["positions_value"],
                daily_return=row["daily_return"] if not pd.isna(row["daily_return"]) else None,
                drawdown=row["drawdown"],
            )

        self._calculate_metrics(equity_df)
        self._calculate_weekly_returns(equity_df)

    def _calculate_metrics(self, equity_df: pd.DataFrame):
        total_return = (self.equity - self.initial_capital) / self.initial_capital

        days = len(equity_df)
        years = days / 252.0 if days > 0 else 1.0
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

        returns = equity_df["daily_return"].dropna()
        sharpe_ratio = None
        if len(returns) > 0 and returns.std() > 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)

        sortino_ratio = None
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0 and downside_returns.std() > 0:
            sortino_ratio = (returns.mean() / downside_returns.std()) * np.sqrt(252)

        max_drawdown = equity_df["drawdown"].max()

        total_trades = len(self.orders_data) // 2
        winning_trades = 0
        losing_trades = 0
        avg_win = 0
        avg_loss = 0

        BacktestMetrics.objects.create(
            strategy_run=self.strategy_run,
            total_return=total_return,
            annual_return=annual_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration_days=None,
            win_rate=0,
            profit_factor=None,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win=avg_win,
            avg_loss=avg_loss,
            avg_trade_duration_minutes=None,
            turnover=sum(o["execution_price"] * o["quantity"] for o in self.orders_data),
            total_commission=sum(o["commission"] for o in self.orders_data),
            total_slippage=0,
            implementation_shortfall_bps=None,
        )

    def _calculate_weekly_returns(self, equity_df: pd.DataFrame):
        equity_df = equity_df.copy()
        equity_df["timestamp"] = pd.to_datetime(equity_df["timestamp"])
        equity_df.set_index("timestamp", inplace=True)

        equity_df["year"] = equity_df.index.isocalendar().year
        equity_df["week"] = equity_df.index.isocalendar().week

        weekly_groups = equity_df.groupby(["year", "week"])

        for (year, week), group in weekly_groups:
            start_equity = group["equity"].iloc[0]
            end_equity = group["equity"].iloc[-1]

            weekly_return = (end_equity - start_equity) / start_equity if start_equity > 0 else 0

            start_date = group.index.min().date()
            end_date = group.index.max().date()

            WeeklyReturn.objects.create(
                strategy_run=self.strategy_run,
                year=year,
                week=week,
                start_date=start_date,
                end_date=end_date,
                weekly_return=weekly_return,
                gross_return=weekly_return,
                net_return=weekly_return,
                trades_count=0,
                turnover=0,
                commission=0,
                slippage=0,
            )
