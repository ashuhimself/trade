from django.db import models

from apps.accounts.models import User


class Strategy(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    class_path = models.CharField(max_length=200)
    parameters = models.JSONField(default=dict)
    universe = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "strategies"
        ordering = ["-created_at"]
        verbose_name_plural = "strategies"

    def __str__(self):
        return self.name


class StrategyRun(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("stopped", "Stopped"),
    ]

    RUN_TYPE_CHOICES = [
        ("backtest", "Backtest"),
        ("paper", "Paper"),
        ("live", "Live"),
    ]

    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, related_name="runs")
    run_type = models.CharField(max_length=20, choices=RUN_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    parameters = models.JSONField(default=dict)
    result = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "strategy_runs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["strategy", "run_type", "status"]),
        ]

    def __str__(self):
        return f"{self.strategy.name} {self.run_type} {self.status}"
