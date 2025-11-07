from datetime import date, timedelta

from celery import shared_task
from django.utils import timezone

from apps.data.loaders import BSEBhavcopyLoader, NSEBhavcopyLoader


@shared_task(queue="data")
def refresh_nse_symbols():
    from apps.data.models import Asset, Exchange

    exchange = Exchange.objects.get(code="NSE")
    active_count = Asset.objects.filter(exchange=exchange, is_active=True).count()

    return {"exchange": "NSE", "active_symbols": active_count}


@shared_task(queue="data")
def download_nse_bhavcopy(trade_date: str = None):
    if trade_date:
        dt = date.fromisoformat(trade_date)
    else:
        dt = date.today() - timedelta(days=1)

    loader = NSEBhavcopyLoader()
    bars_created = loader.load_date(dt)

    return {"date": str(dt), "bars_created": bars_created, "exchange": "NSE"}


@shared_task(queue="data")
def download_bse_bhavcopy(trade_date: str = None):
    if trade_date:
        dt = date.fromisoformat(trade_date)
    else:
        dt = date.today() - timedelta(days=1)

    loader = BSEBhavcopyLoader()
    bars_created = loader.load_date(dt)

    return {"date": str(dt), "bars_created": bars_created, "exchange": "BSE"}


@shared_task(queue="data")
def check_corporate_actions():
    from apps.data.models import CorporateAction

    today = timezone.now().date()
    upcoming = CorporateAction.objects.filter(
        ex_date__gte=today, ex_date__lte=today + timedelta(days=7), is_processed=False
    ).count()

    return {"upcoming_actions": upcoming}


@shared_task(queue="data")
def build_minute_bars(symbol: str, exchange: str = "NSE"):
    from apps.data.models import Asset, Bar

    try:
        asset = Asset.objects.get(symbol=symbol, exchange__code=exchange)
        return {"symbol": symbol, "exchange": exchange, "status": "completed"}
    except Asset.DoesNotExist:
        return {"symbol": symbol, "exchange": exchange, "status": "not_found"}
