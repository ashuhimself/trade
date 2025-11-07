from django.db import models
from django.utils import timezone


class Exchange(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=2)
    timezone = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "exchanges"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class AssetClass(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "asset_classes"
        ordering = ["code"]

    def __str__(self):
        return self.code


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)

    class Meta:
        db_table = "currencies"
        ordering = ["code"]

    def __str__(self):
        return self.code


class Asset(models.Model):
    symbol = models.CharField(max_length=50, db_index=True)
    exchange = models.ForeignKey(Exchange, on_delete=models.PROTECT)
    asset_class = models.ForeignKey(AssetClass, on_delete=models.PROTECT)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    isin = models.CharField(max_length=12, blank=True, db_index=True)
    lot_size = models.IntegerField(default=1)
    tick_size = models.DecimalField(max_digits=10, decimal_places=4, default=0.05)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assets"
        unique_together = [["symbol", "exchange"]]
        ordering = ["symbol"]
        indexes = [
            models.Index(fields=["symbol", "exchange"]),
            models.Index(fields=["exchange", "asset_class"]),
        ]

    def __str__(self):
        return f"{self.symbol}:{self.exchange.code}"


class Bar(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="bars")
    timestamp = models.DateTimeField(db_index=True)
    open = models.DecimalField(max_digits=20, decimal_places=4)
    high = models.DecimalField(max_digits=20, decimal_places=4)
    low = models.DecimalField(max_digits=20, decimal_places=4)
    close = models.DecimalField(max_digits=20, decimal_places=4)
    volume = models.BigIntegerField()
    turnover = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    trades = models.IntegerField(null=True)
    timeframe = models.CharField(max_length=10, default="1D")

    class Meta:
        db_table = "bars"
        unique_together = [["asset", "timestamp", "timeframe"]]
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["asset", "-timestamp"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.asset.symbol} {self.timestamp} {self.timeframe}"


class CorporateAction(models.Model):
    ACTION_TYPES = [
        ("split", "Split"),
        ("dividend", "Dividend"),
        ("bonus", "Bonus"),
        ("rights", "Rights"),
        ("merger", "Merger"),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="corporate_actions")
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    ex_date = models.DateField(db_index=True)
    record_date = models.DateField(null=True)
    payment_date = models.DateField(null=True)
    ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    amount = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    details = models.JSONField(default=dict)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "corporate_actions"
        ordering = ["-ex_date"]
        indexes = [
            models.Index(fields=["asset", "ex_date"]),
        ]

    def __str__(self):
        return f"{self.asset.symbol} {self.action_type} {self.ex_date}"
