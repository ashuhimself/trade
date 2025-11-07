from django.contrib import admin

from .models import Execution, Order, Position, SessionMetrics, Trade


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "strategy_run",
        "asset",
        "side",
        "order_type",
        "quantity",
        "filled_quantity",
        "price",
        "status",
        "created_at",
    ]
    list_filter = ["status", "side", "order_type"]
    search_fields = ["asset__symbol", "broker_order_id"]
    date_hierarchy = "created_at"


@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    list_display = ["order", "quantity", "price", "commission", "total_cost", "executed_at"]
    search_fields = ["order__asset__symbol", "broker_execution_id"]
    date_hierarchy = "executed_at"


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = [
        "strategy_run",
        "asset",
        "quantity",
        "avg_entry_price",
        "current_price",
        "unrealized_pnl",
        "updated_at",
    ]
    search_fields = ["asset__symbol"]


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = [
        "strategy_run",
        "asset",
        "quantity",
        "entry_price",
        "exit_price",
        "pnl",
        "pnl_pct",
        "exited_at",
    ]
    search_fields = ["asset__symbol"]
    date_hierarchy = "exited_at"


@admin.register(SessionMetrics)
class SessionMetricsAdmin(admin.ModelAdmin):
    list_display = [
        "strategy_run",
        "timestamp",
        "equity",
        "unrealized_pnl",
        "realized_pnl",
        "total_orders",
    ]
    date_hierarchy = "timestamp"
