import logging
from datetime import timedelta

from apps.itinerary.models import Itinerary
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger("celery")

DEFAULT_RETRY_DELAY = 10

DAYS_TO_PASS_FOR_CLEAN_UP = 30


@shared_task(bind=True, default_retry_delay=DEFAULT_RETRY_DELAY)
def clean_up_itineraries_task(self):
    """
    Clean up itineraries after 30 days.
    """
    print("Started cleanup itineraries")
    logger.info("Started cleanup itineraries")
    pass
    try:
        one_month_ago = timezone.now() - timedelta(days=DAYS_TO_PASS_FOR_CLEAN_UP)
        Itinerary.objects.filter(created_at__lt=one_month_ago).delete()
        logger.info("Ended itineraries claenup")

    except Exception as exception:
        self.retry(exc=exception)
