from django.urls import path

from . import views

urlpatterns = [
    path("", views.overview, name="overview"),
    path("strategies/", views.strategies_list, name="strategies_list"),
    path("strategies/<int:pk>/", views.strategy_detail, name="strategy_detail"),
    path("backtest/<int:run_id>/", views.backtest_results, name="backtest_results"),
    path("live/", views.live_monitor, name="live_monitor"),
    path("data/", views.data_browser, name="data_browser"),
]
