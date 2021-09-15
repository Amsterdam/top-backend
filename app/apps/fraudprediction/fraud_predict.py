# TODO: Add tests
import glob
import importlib
import logging
import math
import os
from enum import Flag, auto, unique
from unittest.mock import Mock

import requests
from apps.cases.models import Project, Stadium
from apps.fraudprediction.models import FraudPrediction
from django.conf import settings
from django.db import connections
from django.utils.module_loading import import_string
from settings.const import STARTING_FROM_DATE
from utils.queries_bwv import get_bwv_personen, get_bwv_personen_hist
from utils.queries_planner import get_cases_from_bwv
from utils.queries_zaken_api import get_fraudprediction_cases_from_AZA_by_model_name

from .mock import fraud_prediction_onderhuur_results, fraud_prediction_results
from .utils import import_from_settings

LOGGER = logging.getLogger(__name__)
celery_logger = logging.getLogger("celery")

DATABASE_CONFIG = {
    "bwv_adres": {"table_name": "import_adres"},
    "bwv_stadia": {"table_name": "import_stadia"},
    "bwv_wvs": {"table_name": "import_wvs"},
    "bwv_personen_hist": {"table_name": "bwv_personen_hist"},
}
SCORE_STARTING_FROM_DATE = STARTING_FROM_DATE


class FraudPredict:
    def __init__(self, model_name, score_module_path):
        self.model_name = model_name
        self.score_module_path = score_module_path

    def start(self):
        LOGGER.info("Started scoring Logger")
        config = {"databases": self.get_all_database_configs(DATABASE_CONFIG)}
        LOGGER.info("Get all db configs")
        case_ids = self.get_case_ids_to_score()
        LOGGER.info("get case ids to score")
        LOGGER.info(len(case_ids))
        LOGGER.info(case_ids)
        cache_dir = settings.FRAUD_PREDICTION_CACHE_DIR
        self.clear_cache_dir(cache_dir)
        LOGGER.info("Cleared cache")
        # Scoring library is optional for local development. This makes sure it's available.

        try:
            LOGGER.info("Importing scoring library")

            score_module = importlib.import_module(self.score_module_path)
        except ModuleNotFoundError as e:
            LOGGER.error("Could not import library. Scoring failed. {}".format(e))
            return

        try:

            from onderhuur_prediction_model.helper_functions import (
                _strings2flags,
                load_config,
            )

            LOGGER.info("Update config with flags")

            config.update(
                {
                    "flags": _strings2flags(
                        [
                            "ADRES",
                            "STADIA",
                            "WVS",
                            "BAG",
                            "BWV_PERSONEN_HIST",
                        ]
                    )
                }
            )
            print(config)
            scorer = score_module.Scorer(cache_dir=cache_dir, config=config)
            LOGGER.info("init scoring logger")
            results = scorer.score(zaak_ids=case_ids)
            LOGGER.info("retrieved results")
            results = results.to_dict(orient="index")
            LOGGER.info("results to dict")
        except Exception as e:
            LOGGER.error("Could not calculate prediction scores: {}".format(str(e)))
            return

        for case_id in case_ids:
            result = results.get(case_id)
            try:
                self.create_or_update_prediction(case_id, result)
            except Exception as e:
                LOGGER.error(
                    "Could not create or update prediction for {}: {}".format(
                        case_id, str(e)
                    )
                )

        LOGGER.info("Finished scoring..")

    def get_all_database_configs(self, conf={}):
        config = {}
        for key, value in conf.items():
            config[key] = self.get_database_config()
            config[key].update(value)
        return config

    def get_database_config(self):
        config = settings.DATABASES[settings.BWV_DATABASE_NAME]
        config = {
            "host": config.get("HOST"),
            "db": config.get("NAME"),
            "user": config.get("USER"),
            "password": config.get("PASSWORD"),
        }
        return config

    def get_stadia_to_score(self):
        return list(
            dict.fromkeys(
                Stadium.objects.filter(
                    team_settings_list__fraud_prediction_model=self.model_name
                ).values_list("name", flat=True)
            )
        )

    def get_projects_to_score(self):
        return list(
            dict.fromkeys(
                Project.objects.filter(
                    team_settings_list__fraud_prediction_model=self.model_name
                ).values_list("name", flat=True)
            )
        )

    def get_case_ids_to_score(self):
        """
        Returns a list of case ids which are eligible for scoring
        """
        cases = get_cases_from_bwv(
            SCORE_STARTING_FROM_DATE,
            self.get_projects_to_score(),
            self.get_stadia_to_score(),
        )
        case_ids = list(set([case.get("id") for case in cases]))
        return case_ids

    def clear_cache_dir(self, dir):
        """
        Clears the contents of the given directory
        """
        try:
            files = glob.glob(os.path.join(dir, "*"))
            for f in files:
                LOGGER.info("removing {}".format(f))
                os.remove(f)
        except Exception as e:
            LOGGER.error(
                "Something when wrong while removing cached scoring files: {}".format(
                    str(e)
                )
            )

    def clean_dictionary(self, dictionary):
        """
        Replaces dictionary NaN values with 0
        """
        dictionary = dictionary.copy()

        for key, value in dictionary.items():
            if math.isnan(value):
                dictionary[key] = 0.0

        return dictionary

    def create_or_update_prediction(self, case_id, result):
        fraud_probability = result.get("score", 0)
        fraud_prediction = result.get("prediction_woonfraude", False)
        business_rules = result.get("business_rules", {})
        shap_values = result.get("shap_values", {})

        # Cleans the dictionary which might contains NaN (due to a possible bug)
        business_rules = self.clean_dictionary(business_rules)
        shap_values = self.clean_dictionary(shap_values)

        FraudPrediction.objects.update_or_create(
            case_id=case_id,
            defaults={
                "fraud_prediction_model": self.model_name,
                "fraud_probability": fraud_probability,
                "fraud_prediction": fraud_prediction,
                "business_rules": business_rules,
                "shap_values": shap_values,
            },
        )


class FraudPredictAPIBased:
    model_name = None
    MODEL_KEYS = {
        settings.FRAUD_PREDICTION_MODEL_VAKANTIEVERHUUR: [
            "prediction",
            "score",
            "business_rules",
            "shap_values",
        ],
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
        if self.model_name == settings.FRAUD_PREDICTION_MODEL_VAKANTIEVERHUUR:
            return fraud_prediction_results()
        elif self.model_name == settings.FRAUD_PREDICTION_MODEL_ONDERHUUR:
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
            case_ids = self.get_case_ids_to_score(True)
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
        result = self.map_results(result)
        celery_logger.info("fraudpredict task: api_results_to_instances")
        updated_case_ids = self.api_results_to_instances(result)
        celery_logger.info("fraudpredict task: updated case id's")
        celery_logger.info(len(updated_case_ids))

        return {
            "available_cases_count": len(case_ids),
            "cases_updated": updated_case_ids,
        }

    def get_stadia_to_score(self):
        return list(
            dict.fromkeys(
                Stadium.objects.filter(
                    team_settings_list__fraud_prediction_model=self.model_name,
                    team_settings_list__use_zaken_backend=False,
                ).values_list("name", flat=True)
            )
        )

    def get_projects_to_score(self):
        return list(
            dict.fromkeys(
                Project.objects.filter(
                    team_settings_list__fraud_prediction_model=self.model_name,
                    team_settings_list__use_zaken_backend=False,
                ).values_list("name", flat=True)
            )
        )

    def get_case_ids_to_score(self, use_zaken_backend=False):
        """
        Returns a list of case ids which are eligible for scoring
        """
        case_ids = []
        if use_zaken_backend:
            cases = get_fraudprediction_cases_from_AZA_by_model_name(self.model_name)
            case_ids = [case.get("id") for case in cases if case.get("id")]
        else:
            cases = get_cases_from_bwv(
                STARTING_FROM_DATE,
                self.get_projects_to_score(),
                self.get_stadia_to_score(),
            )
            case_ids = list(set([case.get("id") for case in cases]))
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
            if results.get(self.get_fraud_prediction_key(), {}).get(case_id, False)
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
