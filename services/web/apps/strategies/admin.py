from django.contrib import admin

from .models import Strategy, StrategyRun


@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ["name", "class_path", "is_active", "created_by", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]


@admin.register(StrategyRun)
class StrategyRunAdmin(admin.ModelAdmin):
    list_display = ["strategy", "run_type", "status", "start_date", "end_date", "created_at"]
    list_filter = ["run_type", "status"]
    search_fields = ["strategy__name"]
    date_hierarchy = "created_at"
