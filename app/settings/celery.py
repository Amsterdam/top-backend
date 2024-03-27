import os

from celery import Celery
from celery.signals import setup_logging
from celery.result import AsyncResult
from django.utils import timezone


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

app = Celery("proj")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.task_default_queue = 'TOP'

@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig

    from django.conf import settings

    dictConfig(settings.LOGGING)


app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
    return True


def stuck_tasks():
    # Query Celery's task database for tasks that are in progress for more than a certain duration
    threshold_seconds = 10  # Adjust this threshold as needed (e.g., 10 minutes)
    stuck_tasks = []
    for task in app.control.inspect().registered():
        print()
        print(task)

    if stuck_tasks:
        return False
    else:
        return True