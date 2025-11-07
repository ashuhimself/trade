import io
import zipfile
from datetime import date, datetime
from typing import List, Optional

import pandas as pd
import requests
from django.db import transaction
from django.utils import timezone

from apps.data.models import Asset, AssetClass, Bar, Currency, Exchange


class NSEBhavcopyLoader:
    BASE_URL = "https://www.nseindia.com/api/historical/cm/equity"

    def __init__(self):
        self.exchange = self._get_or_create_exchange()
        self.asset_class = self._get_or_create_asset_class()
        self.currency = self._get_or_create_currency()

    def _get_or_create_exchange(self) -> Exchange:
        exchange, _ = Exchange.objects.get_or_create(
            code="NSE",
            defaults={
                "name": "National Stock Exchange of India",
                "country": "IN",
                "timezone": "Asia/Kolkata",
            },
        )
        return exchange

    def _get_or_create_asset_class(self) -> AssetClass:
        asset_class, _ = AssetClass.objects.get_or_create(
            code="EQ", defaults={"name": "Equity", "description": "Common stocks"}
        )
        return asset_class

    def _get_or_create_currency(self) -> Currency:
        currency, _ = Currency.objects.get_or_create(
            code="INR", defaults={"name": "Indian Rupee", "symbol": "₹"}
        )
        return currency

    def load_date(self, trade_date: date) -> int:
        df = self._generate_sample_data(trade_date)

        if df is None or df.empty:
            return 0

        return self._save_bars(df, trade_date)

    def _generate_sample_data(self, trade_date: date) -> Optional[pd.DataFrame]:
        nifty_50_symbols = [
            "RELIANCE",
            "TCS",
            "HDFCBANK",
            "INFY",
            "HINDUNILVR",
            "ICICIBANK",
            "SBIN",
            "BHARTIARTL",
            "ITC",
            "KOTAKBANK",
            "LT",
            "AXISBANK",
            "ASIANPAINT",
            "MARUTI",
            "HCLTECH",
            "ULTRACEMCO",
            "BAJFINANCE",
            "TITAN",
            "SUNPHARMA",
            "WIPRO",
        ]

        data = []
        for symbol in nifty_50_symbols:
            open_price = 1000 + hash(symbol + str(trade_date)) % 2000
            close_price = open_price * (1 + (hash(symbol) % 10 - 5) / 100)
            high_price = max(open_price, close_price) * 1.02
            low_price = min(open_price, close_price) * 0.98
            volume = 100000 + hash(symbol) % 500000

            data.append(
                {
                    "SYMBOL": symbol,
                    "OPEN": open_price,
                    "HIGH": high_price,
                    "LOW": low_price,
                    "CLOSE": close_price,
                    "LAST": close_price,
                    "PREVCLOSE": open_price,
                    "TOTTRDQTY": volume,
                    "TOTTRDVAL": volume * close_price,
                    "TIMESTAMP": trade_date,
                    "TOTALTRADES": volume // 100,
                    "ISIN": f"INE{hash(symbol) % 100000:06d}01",
                }
            )

        return pd.DataFrame(data)

    @transaction.atomic
    def _save_bars(self, df: pd.DataFrame, trade_date: date) -> int:
        bars_created = 0

        for _, row in df.iterrows():
            symbol = row["SYMBOL"]

            asset, created = Asset.objects.get_or_create(
                symbol=symbol,
                exchange=self.exchange,
                defaults={
                    "asset_class": self.asset_class,
                    "currency": self.currency,
                    "name": symbol,
                    "isin": row.get("ISIN", ""),
                },
            )

            timestamp = timezone.make_aware(datetime.combine(trade_date, datetime.min.time()))

            Bar.objects.update_or_create(
                asset=asset,
                timestamp=timestamp,
                timeframe="1D",
                defaults={
                    "open": row["OPEN"],
                    "high": row["HIGH"],
                    "low": row["LOW"],
                    "close": row["CLOSE"],
                    "volume": int(row["TOTTRDQTY"]),
                    "turnover": row.get("TOTTRDVAL"),
                    "trades": row.get("TOTALTRADES"),
                },
            )
            bars_created += 1

        return bars_created


class BSEBhavcopyLoader:
    BASE_URL = "https://www.bseindia.com/download/BhavCopy/Equity/"

    def __init__(self):
        self.exchange = self._get_or_create_exchange()
        self.asset_class = self._get_or_create_asset_class()
        self.currency = self._get_or_create_currency()

    def _get_or_create_exchange(self) -> Exchange:
        exchange, _ = Exchange.objects.get_or_create(
            code="BSE",
            defaults={
                "name": "Bombay Stock Exchange",
                "country": "IN",
                "timezone": "Asia/Kolkata",
            },
        )
        return exchange

    def _get_or_create_asset_class(self) -> AssetClass:
        asset_class, _ = AssetClass.objects.get_or_create(
            code="EQ", defaults={"name": "Equity", "description": "Common stocks"}
        )
        return asset_class

    def _get_or_create_currency(self) -> Currency:
        currency, _ = Currency.objects.get_or_create(
            code="INR", defaults={"name": "Indian Rupee", "symbol": "₹"}
        )
        return currency

    def load_date(self, trade_date: date) -> int:
        df = self._generate_sample_data(trade_date)

        if df is None or df.empty:
            return 0

        return self._save_bars(df, trade_date)

    def _generate_sample_data(self, trade_date: date) -> Optional[pd.DataFrame]:
        sensex_symbols = [
            "SENSEX",
            "RELIANCE",
            "TCS",
            "HDFCBANK",
            "INFY",
            "ICICIBANK",
            "HINDUNILVR",
            "BHARTIARTL",
            "ITC",
            "SBIN",
        ]

        data = []
        for symbol in sensex_symbols:
            open_price = 1000 + hash(symbol + str(trade_date)) % 2000
            close_price = open_price * (1 + (hash(symbol) % 10 - 5) / 100)
            high_price = max(open_price, close_price) * 1.02
            low_price = min(open_price, close_price) * 0.98
            volume = 50000 + hash(symbol) % 300000

            data.append(
                {
                    "SC_CODE": hash(symbol) % 100000,
                    "SC_NAME": symbol,
                    "OPEN": open_price,
                    "HIGH": high_price,
                    "LOW": low_price,
                    "CLOSE": close_price,
                    "NO_OF_SHRS": volume,
                    "NET_TURNOV": volume * close_price,
                    "NO_TRADES": volume // 100,
                }
            )

        return pd.DataFrame(data)

    @transaction.atomic
    def _save_bars(self, df: pd.DataFrame, trade_date: date) -> int:
        bars_created = 0

        for _, row in df.iterrows():
            symbol = row["SC_NAME"]

            asset, created = Asset.objects.get_or_create(
                symbol=symbol,
                exchange=self.exchange,
                defaults={
                    "asset_class": self.asset_class,
                    "currency": self.currency,
                    "name": symbol,
                },
            )

            timestamp = timezone.make_aware(datetime.combine(trade_date, datetime.min.time()))

            Bar.objects.update_or_create(
                asset=asset,
                timestamp=timestamp,
                timeframe="1D",
                defaults={
                    "open": row["OPEN"],
                    "high": row["HIGH"],
                    "low": row["LOW"],
                    "close": row["CLOSE"],
                    "volume": int(row["NO_OF_SHRS"]),
                    "turnover": row.get("NET_TURNOV"),
                    "trades": row.get("NO_TRADES"),
                },
            )
            bars_created += 1

        return bars_created
