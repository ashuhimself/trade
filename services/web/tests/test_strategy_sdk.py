import pytest
from apps.strategies.sdk.risk import FixedRiskSizer, VolatilityRiskSizer
from apps.strategies.sdk.slippage import FixedSlippageModel, VolumeSlippageModel
from apps.strategies.sdk.fees import IndianEquityFeeModel, SimpleFeeModel


class TestRiskSizers:
    def test_fixed_risk_sizer(self):
        sizer = FixedRiskSizer(max_position_pct=0.1)
        quantity = sizer.calculate_position_size(
            symbol="RELIANCE",
            signal_strength=1.0,
            current_price=1000,
            equity=1000000,
            current_position=0,
        )

        assert quantity == 100

    def test_volatility_risk_sizer(self):
        sizer = VolatilityRiskSizer(target_volatility=0.15)
        quantity = sizer.calculate_position_size(
            symbol="RELIANCE",
            signal_strength=1.0,
            current_price=1000,
            equity=1000000,
            current_position=0,
            volatility=0.20,
        )

        assert quantity > 0


class TestSlippageModels:
    def test_fixed_slippage_buy(self):
        model = FixedSlippageModel(slippage_bps=5)
        execution_price = model.apply(price=1000, quantity=100, side="buy")

        assert execution_price == 1000.5

    def test_fixed_slippage_sell(self):
        model = FixedSlippageModel(slippage_bps=5)
        execution_price = model.apply(price=1000, quantity=100, side="sell")

        assert execution_price == 999.5


class TestFeeModels:
    def test_simple_fee_model(self):
        model = SimpleFeeModel(commission_bps=5)
        fees = model.calculate(price=1000, quantity=100, side="buy")

        assert fees == 50.0

    def test_indian_equity_fee_model(self):
        model = IndianEquityFeeModel()
        fees = model.calculate(price=1000, quantity=100, side="buy")

        assert fees > 0
        assert isinstance(fees, float)
