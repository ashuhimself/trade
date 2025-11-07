from rest_framework import serializers

from apps.backtest.models import BacktestMetrics, EquityCurve, WeeklyReturn
from apps.data.models import Asset, Bar, CorporateAction, Exchange
from apps.live.models import Execution, Order, Position, SessionMetrics, Trade
from apps.strategies.models import Strategy, StrategyRun


class ExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exchange
        fields = "__all__"


class AssetSerializer(serializers.ModelSerializer):
    exchange_code = serializers.CharField(source="exchange.code", read_only=True)

    class Meta:
        model = Asset
        fields = "__all__"


class BarSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="asset.symbol", read_only=True)

    class Meta:
        model = Bar
        fields = "__all__"


class CorporateActionSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="asset.symbol", read_only=True)

    class Meta:
        model = CorporateAction
        fields = "__all__"


class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = "__all__"


class StrategyRunSerializer(serializers.ModelSerializer):
    strategy_name = serializers.CharField(source="strategy.name", read_only=True)

    class Meta:
        model = StrategyRun
        fields = "__all__"


class BacktestMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BacktestMetrics
        fields = "__all__"


class EquityCurveSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquityCurve
        fields = "__all__"


class WeeklyReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyReturn
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="asset.symbol", read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class ExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Execution
        fields = "__all__"


class PositionSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="asset.symbol", read_only=True)

    class Meta:
        model = Position
        fields = "__all__"


class TradeSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="asset.symbol", read_only=True)

    class Meta:
        model = Trade
        fields = "__all__"


class SessionMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionMetrics
        fields = "__all__"
