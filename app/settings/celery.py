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
    for task_id in AsyncResult.all().iterkeys():
        task = AsyncResult(task_id)
        print(task)
        if task.state == 'STARTED' and (timezone.now() - task.date_started).total_seconds() > threshold_seconds:
            stuck_tasks.append({
                'task_id': task_id,
                'date_started': task.date_started.isoformat(),
                'state': task.state,
            })

    if stuck_tasks:
        return False
    else:
        return True