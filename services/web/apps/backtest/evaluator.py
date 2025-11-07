from typing import Dict, Optional

import numpy as np
import pandas as pd
from django.conf import settings

from apps.backtest.models import WeeklyReturn
from apps.strategies.models import StrategyRun


class WeeklyTargetEvaluator:
    def __init__(
        self,
        target_weekly_return: float = None,
        max_drawdown: float = None,
        p95_weekly_dd: float = None,
    ):
        self.target_weekly_return = (
            target_weekly_return or settings.TARGET_WEEKLY_RETURN_PCT
        ) / 100.0
        self.max_drawdown = (max_drawdown or settings.MAX_DRAWDOWN_PCT) / 100.0
        self.p95_weekly_dd = (p95_weekly_dd or settings.P95_WEEKLY_DD_PCT) / 100.0

    def evaluate(self, strategy_run: StrategyRun) -> Dict:
        weekly_returns = WeeklyReturn.objects.filter(strategy_run=strategy_run).order_by(
            "year", "week"
        )

        if not weekly_returns.exists():
            return self._empty_result()

        returns_data = [float(wr.weekly_return) for wr in weekly_returns]
        df = pd.DataFrame({"weekly_return": returns_data})

        mean_return = df["weekly_return"].mean()
        median_return = df["weekly_return"].median()
        p95_return = df["weekly_return"].quantile(0.95)
        p99_return = df["weekly_return"].quantile(0.99)
        p5_return = df["weekly_return"].quantile(0.05)

        win_count = (df["weekly_return"] > 0).sum()
        total_weeks = len(df)
        win_rate = win_count / total_weeks if total_weeks > 0 else 0

        wins = df[df["weekly_return"] > 0]["weekly_return"]
        losses = df[df["weekly_return"] < 0]["weekly_return"]

        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = losses.mean() if len(losses) > 0 else 0
        payoff_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0

        cumulative_returns = (1 + df["weekly_return"]).cumprod()
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()

        in_drawdown = drawdown < 0
        drawdown_periods = (in_drawdown != in_drawdown.shift()).cumsum()
        drawdown_durations = (
            drawdown[in_drawdown].groupby(drawdown_periods[in_drawdown]).size()
        )
        max_dd_duration = drawdown_durations.max() if len(drawdown_durations) > 0 else 0
        avg_dd_duration = drawdown_durations.mean() if len(drawdown_durations) > 0 else 0

        turnover = sum(float(wr.turnover) for wr in weekly_returns)
        total_commission = sum(float(wr.commission) for wr in weekly_returns)
        total_slippage = sum(float(wr.slippage) for wr in weekly_returns)

        meets_return_target = mean_return >= self.target_weekly_return
        meets_drawdown_target = max_drawdown >= self.max_drawdown
        meets_p95_target = p5_return >= self.p95_weekly_dd

        all_pass = meets_return_target and meets_drawdown_target and meets_p95_target

        badge = "green" if all_pass else "amber" if meets_return_target else "red"

        return {
            "mean_weekly_return": float(mean_return),
            "median_weekly_return": float(median_return),
            "p95_weekly_return": float(p95_return),
            "p99_weekly_return": float(p99_return),
            "p5_weekly_return": float(p5_return),
            "win_rate": float(win_rate),
            "payoff_ratio": float(payoff_ratio),
            "max_drawdown": float(max_drawdown),
            "max_drawdown_duration_weeks": int(max_dd_duration),
            "avg_drawdown_duration_weeks": float(avg_dd_duration),
            "total_weeks": int(total_weeks),
            "turnover": float(turnover),
            "total_commission": float(total_commission),
            "total_slippage": float(total_slippage),
            "target_weekly_return": float(self.target_weekly_return),
            "meets_return_target": bool(meets_return_target),
            "meets_drawdown_target": bool(meets_drawdown_target),
            "meets_p95_target": bool(meets_p95_target),
            "badge": badge,
        }

    def _empty_result(self):
        return {
            "mean_weekly_return": 0,
            "median_weekly_return": 0,
            "p95_weekly_return": 0,
            "p99_weekly_return": 0,
            "p5_weekly_return": 0,
            "win_rate": 0,
            "payoff_ratio": 0,
            "max_drawdown": 0,
            "max_drawdown_duration_weeks": 0,
            "avg_drawdown_duration_weeks": 0,
            "total_weeks": 0,
            "turnover": 0,
            "total_commission": 0,
            "total_slippage": 0,
            "target_weekly_return": self.target_weekly_return,
            "meets_return_target": False,
            "meets_drawdown_target": False,
            "meets_p95_target": False,
            "badge": "red",
        }
