import logging

from apps.itinerary.models import ItineraryItem
from django.conf import settings
from django.db.models import signals
from django.dispatch import receiver
from tenacity import RetryError
from utils.queries_zaken_api import push_case

logger = logging.getLogger(__name__)

# TODO: Tests for this
# TODO: Should log if a push fails
@receiver(signals.post_save, sender=ItineraryItem)
def create_itinerary_item_signal(instance, created, **kwargs):
    if created and instance.case:
        try:
            case_id = instance.case.case_id
            logger.info(f"Signal for pushing case {case_id}")
            if settings.PUSH_ZAKEN:
                push_case(case_id)
        except RetryError as e:
            logger.error(f"Pushing case failed: {str(e)}")
