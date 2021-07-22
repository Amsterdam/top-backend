from apps.itinerary.models import ItineraryItem
from apps.itinerary.tasks import push_itinerary_item
from django.conf import settings
from django.db import transaction
from django.db.models import signals
from django.dispatch import receiver
from tenacity import RetryError

# TODO: Tests for this
# TODO: Do we need this
# @receiver(signals.post_save, sender=ItineraryItem)
# def create_itinerary_item_signal(instance, created, **kwargs):
#     """ Pushes the ItineraryItem and Case data to zaken app using a Celery task"""
#     if created and instance.case:
#         task = push_itinerary_item.s(instance.pk).delay
#         transaction.on_commit(task)
