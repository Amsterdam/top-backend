import logging
import math
import os

import requests
from apps.cases.models import Project, Stadium
from apps.fraudprediction.models import FraudPrediction
from apps.fraudprediction.serializers import FraudPredictionSerializer
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from settings.const import STARTING_FROM_DATE
from utils.queries_planner import get_cases_from_bwv
from utils.queries_zaken_api import get_fraudprediction_cases_from_AZA_by_model_name

from .mock import fraud_prediction_results

LOGGER = logging.getLogger("celery")


def get_fraud_prediction(case_id):
    try:
        fraud_prediction = FraudPrediction.objects.get(case_id=case_id)
        serializer = FraudPredictionSerializer(fraud_prediction)
        return serializer.data
    except FraudPrediction.DoesNotExist:
        LOGGER.warning(
            "Fraud prediction object for case does not exist: {}".format(case_id)
        )


def get_fraud_predictions():
    """
    Returns a dictionary of all fraud predictions mapped to case_ids
    """
    fraud_predictions = FraudPrediction.objects.all()
    fraud_prediction_dictionary = {}

    for fraud_prediction in fraud_predictions:
        fraud_prediction_dictionary[
            str(fraud_prediction.case_id)
        ] = FraudPredictionSerializer(fraud_prediction).data

    return fraud_prediction_dictionary


def add_fraud_predictions(cases):
    """
    Returns a list of case dictionaries, enriched with fraud_predictions
    """
    cases = cases.copy()

    for case in cases:
        case_id = case.get("id")
        case["fraud_prediction"] = get_fraud_prediction(case_id)

    return cases


def import_from_settings(attr, *args):
    """
    Load an attribute from the django settings.
    :raises:
        ImproperlyConfigured
    """
    try:
        if args:
            return getattr(settings, attr, args[0])
        return getattr(settings, attr)
    except AttributeError:
        raise ImproperlyConfigured("Setting {0} not found".format(attr))
