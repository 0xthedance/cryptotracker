import os
import logging

from logging.config import dictConfig
from django.conf import settings

from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging, task_failure

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


@setup_logging.connect
def config_loggers(*args, **kwargs):

    dictConfig(settings.LOGGING)

@task_failure.connect
def log_task_failure(sender=None, task_id=None, exception=None, 
                     args=None, kwargs=None, traceback=None, **extra):
    logger = logging.getLogger('celery')
    logger.error(
        f'Task failure: {sender.name}',
        extra={
            'task_id': task_id,
            'task_args': args,
            'task_kwargs': kwargs,
        },
        exc_info=(type(exception), exception, traceback)
    )