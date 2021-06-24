import logging
import os

import requests
from apps.fraudprediction.fraud_predict import FraudPredict, FraudPredictAPIBased
from celery import shared_task
from django.conf import settings

from .mock import fraud_prediction_results
from .utils import fraudpredict_vakantieverhuur

logger = logging.getLogger("celery")

DEFAULT_RETRY_DELAY = 10


@shared_task(bind=True, default_retry_delay=DEFAULT_RETRY_DELAY)
def fraudpredict_vakantieverhuur_task(self):
    """
    Calculate fraudpredictions for vakantieverhuur
    """

    try:
        logger.info("Started fraudpredict vakantieverhuur task")

        prediction_instance = FraudPredictAPIBased(
            settings.FRAUD_PREDICTION_MODEL_VAKANTIEVERHUUR
        )
        result = prediction_instance.fraudpredict()

        logger.info("Ended fraudpredict vakantieverhuur task")

    except Exception as exception:
        self.retry(exc=exception)

    return result


@shared_task(bind=True, default_retry_delay=DEFAULT_RETRY_DELAY)
def fraudpredict_onderhuur_task(self):
    """
    Calculate fraudpredictions for onderhuur
    """

    try:
        logger.info("Started fraudpredict onderhuur task")

        prediction_instance = FraudPredictAPIBased(
            settings.FRAUD_PREDICTION_MODEL_ONDERHUUR
        )
        result = prediction_instance.fraudpredict()

        logger.info("Ended fraudpredict onderhuur task")

    except Exception as exception:
        self.retry(exc=exception)

    return result
