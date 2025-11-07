from django.contrib import admin

from .models import Asset, AssetClass, Bar, CorporateAction, Currency, Exchange


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "country", "timezone", "is_active"]
    list_filter = ["country", "is_active"]
    search_fields = ["code", "name"]


@admin.register(AssetClass)
class AssetClassAdmin(admin.ModelAdmin):
    list_display = ["code", "name"]
    search_fields = ["code", "name"]


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "symbol"]
    search_fields = ["code", "name"]


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ["symbol", "exchange", "asset_class", "currency", "is_active"]
    list_filter = ["exchange", "asset_class", "is_active"]
    search_fields = ["symbol", "name", "isin"]


@admin.register(Bar)
class BarAdmin(admin.ModelAdmin):
    list_display = ["asset", "timestamp", "timeframe", "open", "high", "low", "close", "volume"]
    list_filter = ["timeframe", "asset__exchange"]
    search_fields = ["asset__symbol"]
    date_hierarchy = "timestamp"


@admin.register(CorporateAction)
class CorporateActionAdmin(admin.ModelAdmin):
    list_display = ["asset", "action_type", "ex_date", "ratio", "amount", "is_processed"]
    list_filter = ["action_type", "is_processed"]
    search_fields = ["asset__symbol"]
    date_hierarchy = "ex_date"
