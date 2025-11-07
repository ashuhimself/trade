from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .viewsets import (
    AssetViewSet,
    BarViewSet,
    CorporateActionViewSet,
    ExchangeViewSet,
    OrderViewSet,
    PositionViewSet,
    StrategyRunViewSet,
    StrategyViewSet,
    TradeViewSet,
)

router = DefaultRouter()
router.register(r"exchanges", ExchangeViewSet)
router.register(r"assets", AssetViewSet)
router.register(r"bars", BarViewSet)
router.register(r"corporate-actions", CorporateActionViewSet)
router.register(r"strategies", StrategyViewSet)
router.register(r"strategy-runs", StrategyRunViewSet)
router.register(r"orders", OrderViewSet)
router.register(r"positions", PositionViewSet)
router.register(r"trades", TradeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
