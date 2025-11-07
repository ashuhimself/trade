from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.backtest.models import BacktestMetrics, EquityCurve, WeeklyReturn
from apps.backtest.evaluator import WeeklyTargetEvaluator
from apps.data.models import Asset, Bar, CorporateAction, Exchange
from apps.live.models import Order, Position, Trade
from apps.strategies.models import Strategy, StrategyRun

from .serializers import (
    AssetSerializer,
    BacktestMetricsSerializer,
    BarSerializer,
    CorporateActionSerializer,
    EquityCurveSerializer,
    ExchangeSerializer,
    OrderSerializer,
    PositionSerializer,
    StrategyRunSerializer,
    StrategySerializer,
    TradeSerializer,
    WeeklyReturnSerializer,
)


class ExchangeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exchange.objects.all()
    serializer_class = ExchangeSerializer
    filter_backends = [filters.OrderingFilter]


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ["exchange", "asset_class", "is_active"]
    search_fields = ["symbol", "name", "isin"]


class BarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bar.objects.all()
    serializer_class = BarSerializer
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ["asset", "timeframe"]
    ordering_fields = ["timestamp"]


class CorporateActionViewSet(viewsets.ModelViewSet):
    queryset = CorporateAction.objects.all()
    serializer_class = CorporateActionSerializer
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ["asset", "action_type", "is_processed"]


class StrategyViewSet(viewsets.ModelViewSet):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ["is_active"]


class StrategyRunViewSet(viewsets.ModelViewSet):
    queryset = StrategyRun.objects.all()
    serializer_class = StrategyRunSerializer
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ["strategy", "run_type", "status"]

    @action(detail=True, methods=["get"])
    def metrics(self, request, pk=None):
        strategy_run = self.get_object()

        try:
            backtest_metrics = BacktestMetrics.objects.get(strategy_run=strategy_run)
            metrics_serializer = BacktestMetricsSerializer(backtest_metrics)
        except BacktestMetrics.DoesNotExist:
            return Response({"detail": "Metrics not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(metrics_serializer.data)

    @action(detail=True, methods=["get"])
    def equity_curve(self, request, pk=None):
        strategy_run = self.get_object()
        equity_curve = EquityCurve.objects.filter(strategy_run=strategy_run).order_by("timestamp")
        serializer = EquityCurveSerializer(equity_curve, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def weekly_returns(self, request, pk=None):
        strategy_run = self.get_object()
        weekly_returns = WeeklyReturn.objects.filter(strategy_run=strategy_run).order_by(
            "year", "week"
        )
        serializer = WeeklyReturnSerializer(weekly_returns, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def evaluate(self, request, pk=None):
        strategy_run = self.get_object()
        evaluator = WeeklyTargetEvaluator()
        result = evaluator.evaluate(strategy_run)
        return Response(result)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        strategy_run = self.get_object()

        if strategy_run.status not in ["pending", "stopped"]:
            return Response(
                {"detail": "Can only start pending or stopped runs"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if strategy_run.run_type == "backtest":
            from apps.backtest.tasks import run_backtest

            run_backtest.delay(strategy_run.id)
        else:
            return Response(
                {"detail": "Live and paper runs not yet implemented"},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        strategy_run.status = "running"
        strategy_run.save()

        return Response({"status": "started"})


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ["strategy_run", "asset", "status", "side"]


class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ["strategy_run", "asset"]


class TradeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ["strategy_run", "asset"]
