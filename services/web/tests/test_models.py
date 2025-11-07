import pytest
from datetime import date
from django.utils import timezone

from apps.data.models import Asset, AssetClass, Currency, Exchange, Bar


@pytest.mark.django_db
class TestDataModels:
    def test_create_exchange(self):
        exchange = Exchange.objects.create(
            code="NSE",
            name="National Stock Exchange",
            country="IN",
            timezone="Asia/Kolkata"
        )
        assert exchange.code == "NSE"
        assert exchange.is_active is True

    def test_create_asset(self):
        exchange = Exchange.objects.create(
            code="NSE", name="NSE", country="IN", timezone="Asia/Kolkata"
        )
        asset_class = AssetClass.objects.create(code="EQ", name="Equity")
        currency = Currency.objects.create(code="INR", name="Rupee", symbol="₹")

        asset = Asset.objects.create(
            symbol="RELIANCE",
            exchange=exchange,
            asset_class=asset_class,
            currency=currency,
            name="Reliance Industries",
        )

        assert asset.symbol == "RELIANCE"
        assert str(asset) == "RELIANCE:NSE"

    def test_create_bar(self):
        exchange = Exchange.objects.create(
            code="NSE", name="NSE", country="IN", timezone="Asia/Kolkata"
        )
        asset_class = AssetClass.objects.create(code="EQ", name="Equity")
        currency = Currency.objects.create(code="INR", name="Rupee", symbol="₹")
        asset = Asset.objects.create(
            symbol="RELIANCE",
            exchange=exchange,
            asset_class=asset_class,
            currency=currency,
            name="Reliance",
        )

        bar = Bar.objects.create(
            asset=asset,
            timestamp=timezone.now(),
            open=1000,
            high=1050,
            low=990,
            close=1020,
            volume=100000,
            timeframe="1D",
        )

        assert bar.asset == asset
        assert bar.close == 1020
