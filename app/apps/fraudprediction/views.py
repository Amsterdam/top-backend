# TODO: Add tests
import logging
import os
from datetime import datetime
from multiprocessing import Process

from apps.fraudprediction.fraud_predict import FraudPredict
from apps.fraudprediction.permissions import FraudPredictionApiKeyAuth
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet

LOGGER = logging.getLogger(__name__)


class FraudPredictionScoringViewSet(ViewSet):
    """
    A view for triggering fraud scoring
    """

    permission_classes = [FraudPredictionApiKeyAuth | IsAuthenticated]

    def background_process(self):
        LOGGER.info("Started scoring background process")

        if hasattr(os, "getppid"):
            LOGGER.info("Scoring process: {}".format(os.getpid()))

        fraud_predict = FraudPredict()
        fraud_predict.start()

        LOGGER.info("Finished scoring background process")

    def create(self, request):
        if hasattr(os, "getppid"):
            LOGGER.info("Process kicking off scoring: {}".format(os.getpid()))

        p = Process(target=self.background_process)
        p.start()

        json = {
            "message": "Scoring Started {}".format(str(datetime.now())),
        }
        return JsonResponse(json)
