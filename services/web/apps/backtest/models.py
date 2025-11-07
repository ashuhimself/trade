from django.db import models

from apps.strategies.models import StrategyRun


class BacktestMetrics(models.Model):
    strategy_run = models.OneToOneField(
        StrategyRun, on_delete=models.CASCADE, related_name="backtest_metrics"
    )
    total_return = models.DecimalField(max_digits=10, decimal_places=4)
    annual_return = models.DecimalField(max_digits=10, decimal_places=4)
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    sortino_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=4)
    max_drawdown_duration_days = models.IntegerField(null=True)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2)
    profit_factor = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    total_trades = models.IntegerField()
    winning_trades = models.IntegerField()
    losing_trades = models.IntegerField()
    avg_win = models.DecimalField(max_digits=20, decimal_places=4)
    avg_loss = models.DecimalField(max_digits=20, decimal_places=4)
    avg_trade_duration_minutes = models.FloatField(null=True)
    turnover = models.DecimalField(max_digits=20, decimal_places=2)
    total_commission = models.DecimalField(max_digits=20, decimal_places=4)
    total_slippage = models.DecimalField(max_digits=20, decimal_places=4)
    implementation_shortfall_bps = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        db_table = "backtest_metrics"

    def __str__(self):
        return f"Metrics for {self.strategy_run}"


class EquityCurve(models.Model):
    strategy_run = models.ForeignKey(
        StrategyRun, on_delete=models.CASCADE, related_name="equity_curve"
    )
    timestamp = models.DateTimeField(db_index=True)
    equity = models.DecimalField(max_digits=20, decimal_places=4)
    cash = models.DecimalField(max_digits=20, decimal_places=4)
    positions_value = models.DecimalField(max_digits=20, decimal_places=4)
    daily_return = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    drawdown = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        db_table = "equity_curves"
        unique_together = [["strategy_run", "timestamp"]]
        ordering = ["timestamp"]
        indexes = [
            models.Index(fields=["strategy_run", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.strategy_run} {self.timestamp}"


class WeeklyReturn(models.Model):
    strategy_run = models.ForeignKey(
        StrategyRun, on_delete=models.CASCADE, related_name="weekly_returns"
    )
    year = models.IntegerField()
    week = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    weekly_return = models.DecimalField(max_digits=10, decimal_places=4)
    gross_return = models.DecimalField(max_digits=10, decimal_places=4)
    net_return = models.DecimalField(max_digits=10, decimal_places=4)
    trades_count = models.IntegerField(default=0)
    turnover = models.DecimalField(max_digits=20, decimal_places=2)
    commission = models.DecimalField(max_digits=20, decimal_places=4)
    slippage = models.DecimalField(max_digits=20, decimal_places=4)

    class Meta:
        db_table = "weekly_returns"
        unique_together = [["strategy_run", "year", "week"]]
        ordering = ["year", "week"]
        indexes = [
            models.Index(fields=["strategy_run", "year", "week"]),
        ]

    def __str__(self):
        return f"{self.strategy_run} {self.year}-W{self.week}"
