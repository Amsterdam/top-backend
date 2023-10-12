# TODO: Add tests
import logging
import os

import requests
from apps.fraudprediction.models import FraudPrediction
from django.conf import settings
from utils.queries_zaken_api import get_fraudprediction_cases_from_AZA_by_model_name

from .mock import fraud_prediction_onderhuur_results, fraud_prediction_results
from .utils import import_from_settings

LOGGER = logging.getLogger(__name__)
celery_logger = logging.getLogger("celery")


class FraudPredictAPIBased:
    model_name = None
    MODEL_KEYS = {
        settings.FRAUD_PREDICTION_MODEL_ONDERHUUR: [
            "snapshot",
            "br_count",
            "ci_count",
            "sum_br_w",
            "prediction",
            "score",
            "business_rules",
            "shap_values",
        ],
    }

    def __init__(self, model_name=None):
        if model_name:
            self.model_name = model_name
        if not self.model_name:
            raise NotImplementedError("Instance needs a fraudprediction model name")

    def get_settings(self, settings_key):
        return import_from_settings(f"{self.model_name.upper()}_{settings_key}")

    def get_mock_data(self):
        if self.model_name == settings.FRAUD_PREDICTION_MODEL_ONDERHUUR:
            return fraud_prediction_onderhuur_results()

    def fraudpredict(self):
        """
        Calculate fraudpredictions
        """
        CONNECT_TIMEOUT = 10
        READ_TIMEOUT = 60

        celery_logger.info(self.model_name)
        celery_logger.info(os.environ)
        case_ids = []
        celery_logger.info("fraudpredict task: case id count")
        celery_logger.info(len(case_ids))
        celery_logger.info("fraudpredict task: case ids")
        celery_logger.info(case_ids)
        if settings.USE_HITKANS_MOCK_DATA:
            celery_logger.info("fraudpredict task: use mock data")
            result = self.get_mock_data()
        else:
            case_ids = self.get_case_ids_to_score()
            data = {
                "zaken_ids": case_ids,
                "auth_token": self.get_settings("HITKANS_AUTH_TOKEN"),
            }

            response = requests.post(
                self.get_settings("HITKANS_API_BASE") + "/score_zaken",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                json=data,
                headers={
                    "content-type": "application/json",
                },
            )
            response.raise_for_status()
            celery_logger.info("fraudpredict task: response status")
            celery_logger.info(response.status_code)
            celery_logger.info("fraudpredict task: response json")
            celery_logger.info(response.json())
            result = response.json()

        celery_logger.info("fraudpredict task: map_results")
        mapped_result = self.map_results(result)
        celery_logger.info("fraudpredict task: api_results_to_instances")
        updated_case_ids = self.api_results_to_instances(mapped_result)
        celery_logger.info("fraudpredict task: updated case id's")
        celery_logger.info(len(updated_case_ids))

        result_keys = list(result.keys())
        result_case_ids = list(result.get(result_keys[0], {}).keys())

        mapped_result_case_ids = list(mapped_result.keys())

        return {
            "available_cases_count": len(case_ids),
            "available_cases": case_ids,
            "result_count": len(result_case_ids),
            "result": result,
            "mapped_result_count": len(mapped_result_case_ids),
            "mapped_result": mapped_result,
            "updated_cases_count": len(updated_case_ids),
            "updated_cases": updated_case_ids,
        }

    def get_case_ids_to_score(self):
        """
        Returns a list of case ids which are eligible for scoring
        """
        case_ids = []
        cases = get_fraudprediction_cases_from_AZA_by_model_name(self.model_name)
        case_ids = [case.get("id") for case in cases if case.get("id")]
        return case_ids

    def get_model_keys(self):
        return self.MODEL_KEYS.get(self.model_name, [])

    def map_results(self, results):
        keys = list(results.keys())
        if not keys:
            return {}
        return dict(
            (
                case_id,
                {
                    "fraud_prediction_model": self.model_name,
                    "fraud_probability": results.get(
                        self.get_fraud_probability_key(), {}
                    ).get(case_id, 0),
                    "fraud_prediction": results.get(
                        self.get_fraud_prediction_key(), {}
                    ).get(case_id, False),
                    "business_rules": self.clean_dictionary(
                        results.get(self.get_business_rules_key(), {}).get(case_id, {})
                    ),
                    "shap_values": self.clean_dictionary(
                        results.get(self.get_shap_values_key(), {}).get(case_id, {})
                    ),
                },
            )
            for case_id in results.get(keys[0], {}).keys()
        )

    def get_fraud_probability_key(self):
        return "score"

    def get_fraud_prediction_key(self):
        return "prediction"

    def get_business_rules_key(self):
        return "business_rules"

    def get_shap_values_key(self):
        return "shap_values"

    def api_results_to_instances(self, results):
        for case_id, result in results.items():
            FraudPrediction.objects.update_or_create(
                case_id=case_id,
                defaults=result,
            )
        return list(results.keys())

    def clean_dictionary(self, dictionary):
        """
        Replaces dictionary NaN values with 0
        """
        dictionary = dictionary.copy()

        for key, value in dictionary.items():
            if type(value) == int or type(value) == float:
                pass
            else:
                dictionary[key] = 0.0

        return dictionary
