from django.contrib import admin

from .models import BacktestMetrics, EquityCurve, WeeklyReturn


@admin.register(BacktestMetrics)
class BacktestMetricsAdmin(admin.ModelAdmin):
    list_display = [
        "strategy_run",
        "total_return",
        "sharpe_ratio",
        "max_drawdown",
        "win_rate",
        "total_trades",
    ]
    search_fields = ["strategy_run__strategy__name"]


@admin.register(EquityCurve)
class EquityCurveAdmin(admin.ModelAdmin):
    list_display = ["strategy_run", "timestamp", "equity", "cash", "drawdown"]
    search_fields = ["strategy_run__strategy__name"]
    date_hierarchy = "timestamp"


@admin.register(WeeklyReturn)
class WeeklyReturnAdmin(admin.ModelAdmin):
    list_display = [
        "strategy_run",
        "year",
        "week",
        "start_date",
        "end_date",
        "weekly_return",
        "trades_count",
    ]
    list_filter = ["year"]
    search_fields = ["strategy_run__strategy__name"]
