import logging

from apps.fraudprediction.models import FraudPrediction
from apps.itinerary.tasks import push_visit
from apps.visits.models import Visit, VisitMetaData
from django.conf import settings
from django.db import transaction
from django.db.models import signals
from django.dispatch import receiver

logger = logging.getLogger(__name__)


# @receiver(signals.post_save, sender=Visit)
# def update_openzaken_system(sender, instance, created, **kwargs):
#     """ Updates or creates a visit in the the Zaken app using a Celery task"""
#     task = push_visit.s(visit_id=instance.id, created=created).delay
#     transaction.on_commit(task)


# @receiver(signals.post_save, sender=Visit)
# def post_save_visit(sender, instance, **kwargs):
#     """ Capture meta data after a visit is created or updated """
#     capture_visit_meta_data(instance)


# def capture_visit_meta_data(visit):
#     """ Captures visit data """
#     visit_meta_data = VisitMetaData.objects.get_or_create(visit=visit)[0]

#     try:
#         fraud_prediction = visit.itinerary_item.case.fraud_prediction
#     except FraudPrediction.DoesNotExist:
#         return

#     # Add visit data to persist it as judicial documentation
#     visit_meta_data.fraud_probability = fraud_prediction.fraud_probability
#     visit_meta_data.fraud_prediction_business_rules = fraud_prediction.business_rules
#     visit_meta_data.fraud_prediction_shap_values = fraud_prediction.shap_values
#     visit_meta_data.save()
