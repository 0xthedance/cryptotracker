import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dcp.settings")
app = Celery("dcp")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.beat_schedule = {
    "fetch-assets-every-24-hours": {
        "task": "cryptotracker.tasks.update_asses_database",
        "schedule": crontab(hour=0, minute=0),
    },
    "fetch-staking-every-24-hours": {
        "task": "cryptotracker.tasks.update_staking_assets",
        "schedule": crontab(hour=0, minute=0),
    },
    "fetch-cryptocurrency-price-every-24-hours": {
        "task": "cryptotracker.tasks.update_cryptocurrency_price",
        "schedule": crontab(hour=0, minute=1),
    },
}
app.autodiscover_tasks()
