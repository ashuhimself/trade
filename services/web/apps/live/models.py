from django.db import models

from apps.data.models import Asset
from apps.strategies.models import StrategyRun


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ("market", "Market"),
        ("limit", "Limit"),
        ("stop_loss", "Stop Loss"),
        ("stop_loss_market", "Stop Loss Market"),
    ]

    SIDE_CHOICES = [
        ("buy", "Buy"),
        ("sell", "Sell"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("submitted", "Submitted"),
        ("partial", "Partial"),
        ("filled", "Filled"),
        ("cancelled", "Cancelled"),
        ("rejected", "Rejected"),
    ]

    strategy_run = models.ForeignKey(StrategyRun, on_delete=models.CASCADE, related_name="orders")
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES)
    side = models.CharField(max_length=10, choices=SIDE_CHOICES)
    quantity = models.IntegerField()
    filled_quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    trigger_price = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    avg_fill_price = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    broker_order_id = models.CharField(max_length=100, blank=True, db_index=True)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True)
    filled_at = models.DateTimeField(null=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["strategy_run", "status"]),
            models.Index(fields=["asset", "created_at"]),
        ]

    def __str__(self):
        return f"{self.side} {self.quantity} {self.asset.symbol} @ {self.price}"


class Execution(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="executions")
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=20, decimal_places=4)
    commission = models.DecimalField(max_digits=20, decimal_places=4)
    exchange_fee = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    stt = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    gst = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    total_cost = models.DecimalField(max_digits=20, decimal_places=4)
    broker_execution_id = models.CharField(max_length=100, blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "executions"
        ordering = ["-executed_at"]

    def __str__(self):
        return f"{self.order} - {self.quantity} @ {self.price}"


class Position(models.Model):
    strategy_run = models.ForeignKey(StrategyRun, on_delete=models.CASCADE, related_name="positions")
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    avg_entry_price = models.DecimalField(max_digits=20, decimal_places=4)
    current_price = models.DecimalField(max_digits=20, decimal_places=4)
    unrealized_pnl = models.DecimalField(max_digits=20, decimal_places=4)
    realized_pnl = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    opened_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True)

    class Meta:
        db_table = "positions"
        unique_together = [["strategy_run", "asset"]]
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["strategy_run", "asset"]),
        ]

    def __str__(self):
        return f"{self.asset.symbol} {self.quantity}"


class Trade(models.Model):
    strategy_run = models.ForeignKey(StrategyRun, on_delete=models.CASCADE, related_name="trades")
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    entry_price = models.DecimalField(max_digits=20, decimal_places=4)
    exit_price = models.DecimalField(max_digits=20, decimal_places=4)
    entry_commission = models.DecimalField(max_digits=20, decimal_places=4)
    exit_commission = models.DecimalField(max_digits=20, decimal_places=4)
    slippage = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    pnl = models.DecimalField(max_digits=20, decimal_places=4)
    pnl_pct = models.DecimalField(max_digits=10, decimal_places=4)
    duration_minutes = models.IntegerField()
    entry_order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, related_name="entry_trades"
    )
    exit_order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, related_name="exit_trades"
    )
    entered_at = models.DateTimeField()
    exited_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "trades"
        ordering = ["-exited_at"]
        indexes = [
            models.Index(fields=["strategy_run", "exited_at"]),
        ]

    def __str__(self):
        return f"{self.asset.symbol} PnL: {self.pnl}"


class SessionMetrics(models.Model):
    strategy_run = models.ForeignKey(StrategyRun, on_delete=models.CASCADE, related_name="session_metrics")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    equity = models.DecimalField(max_digits=20, decimal_places=4)
    cash = models.DecimalField(max_digits=20, decimal_places=4)
    positions_value = models.DecimalField(max_digits=20, decimal_places=4)
    unrealized_pnl = models.DecimalField(max_digits=20, decimal_places=4)
    realized_pnl = models.DecimalField(max_digits=20, decimal_places=4)
    total_orders = models.IntegerField(default=0)
    filled_orders = models.IntegerField(default=0)
    rejected_orders = models.IntegerField(default=0)
    avg_latency_ms = models.FloatField(null=True)
    max_latency_ms = models.FloatField(null=True)

    class Meta:
        db_table = "session_metrics"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["strategy_run", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.strategy_run} {self.timestamp}"
