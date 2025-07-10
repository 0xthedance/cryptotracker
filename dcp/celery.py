import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dcp.settings")
app = Celery("dcp")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.beat_schedule = {
    "daily-snapshot-update": {
        "task": "cryptotracker.tasks.run_daily_snapshot_update",
        "schedule": crontab(hour=0, minute=0),
    },
}

app.autodiscover_tasks()
