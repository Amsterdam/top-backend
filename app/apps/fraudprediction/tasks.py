import logging

from apps.fraudprediction.fraud_predict import FraudPredictAPIBased
from celery import shared_task
from django.conf import settings

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
            model_name=settings.FRAUD_PREDICTION_MODEL_VAKANTIEVERHUUR,
            use_zaken_backend=True,
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
            model_name=settings.FRAUD_PREDICTION_MODEL_ONDERHUUR,
            use_zaken_backend=False,
        )
        result = prediction_instance.fraudpredict()

        logger.info("Ended fraudpredict onderhuur task")

    except Exception as exception:
        self.retry(exc=exception)

    return result
