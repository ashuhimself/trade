import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("trading_platform")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "refresh-nse-symbols": {
        "task": "apps.data.tasks.refresh_nse_symbols",
        "schedule": crontab(hour=6, minute=0, day_of_week="mon-fri"),
    },
    "download-nse-bhavcopy": {
        "task": "apps.data.tasks.download_nse_bhavcopy",
        "schedule": crontab(hour=18, minute=30, day_of_week="mon-fri"),
    },
    "download-bse-bhavcopy": {
        "task": "apps.data.tasks.download_bse_bhavcopy",
        "schedule": crontab(hour=18, minute=45, day_of_week="mon-fri"),
    },
    "check-corporate-actions": {
        "task": "apps.data.tasks.check_corporate_actions",
        "schedule": crontab(hour=7, minute=0, day_of_week="mon-fri"),
    },
}
