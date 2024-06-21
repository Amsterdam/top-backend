import logging
from datetime import timedelta

from apps.itinerary.models import Itinerary
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger("celery")

DEFAULT_RETRY_DELAY = 10
DAYS_UNTIL_DELETION = 30


@shared_task(bind=True, default_retry_delay=DEFAULT_RETRY_DELAY)
def clean_up_itineraries_task(self):
    """
    Clean up itineraries older than 30 days.
    """
    logger.info("Started cleanup of itineraries")

    try:
        one_month_ago = timezone.now() - timedelta(days=DAYS_UNTIL_DELETION)
        deleted_count, _ = Itinerary.objects.filter(
            created_at__lt=one_month_ago
        ).delete()
        logger.info(f"Ended itineraries cleanup, deleted {deleted_count} itineraries")

    except Exception as exception:
        logger.error(f"Exception occurred during itineraries cleanup: {exception}")
        self.retry(exc=exception)
