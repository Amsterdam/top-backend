# TODO: Add tests
import glob
import logging
import math
import os
from unittest.mock import Mock

from apps.fraudprediction.models import FraudPrediction
from django.conf import settings
from django.db import connections
from settings.const import PROJECTS, STADIA, STARTING_FROM_DATE
from utils.queries_planner import get_cases_from_bwv

LOGGER = logging.getLogger(__name__)

DATABASE_CONFIG_KEYS = [
    "adres",
    "bwv_adres_periodes",
    "bbga",
    "hotline",
    "personen",
    "personen_hist",
    "stadia",
    "zaken",
]
SCORE_STARTING_FROM_DATE = STARTING_FROM_DATE


class FraudPredict:
    def start(self):
        LOGGER.info("Started scoring Logger")
        dbconfig = self.get_all_database_configs(DATABASE_CONFIG_KEYS)
        LOGGER.info("Get all db configs")
        case_ids = self.get_case_ids_to_score()
        LOGGER.info("get case ids to score")
        cache_dir = settings.FRAUD_PREDICTION_CACHE_DIR
        self.clear_cache_dir(cache_dir)
        LOGGER.info("Cleared cache")

        # Scoring library is optional for local development. This makes sure it's available.
        try:
            LOGGER.info("Importing scoring library")
            from woonfraude_model import score
        except ModuleNotFoundError as e:
            LOGGER.error("Could not import library. Scoring failed. {}".format(e))
            return

        try:
            scorer = score.Scorer(cache_dir=cache_dir, dbconfig=dbconfig)
            LOGGER.info("init scoring logger")
            results = scorer.score(
                zaak_ids=case_ids, zaken_con=connections[settings.BWV_DATABASE_NAME]
            )
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

    def get_all_database_configs(self, keys=[]):
        config = {}
        for key in keys:
            config[key] = self.get_database_config()
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

    def get_case_ids_to_score(self):
        """
        Returns a list of case ids which are eligible for scoring
        """
        cases = get_cases_from_bwv(SCORE_STARTING_FROM_DATE, PROJECTS, STADIA)
        case_ids = [case.get("case_id") for case in cases]
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
        fraud_probability = result.get("prob_woonfraude")
        fraud_prediction = result.get("prediction_woonfraude")
        business_rules = result.get("business_rules")
        shap_values = result.get("shap_values")

        # Cleans the dictionary which might contains NaN (due to a possible bug)
        business_rules = self.clean_dictionary(business_rules)
        shap_values = self.clean_dictionary(shap_values)

        FraudPrediction.objects.update_or_create(
            case_id=case_id,
            defaults={
                "fraud_probability": fraud_probability,
                "fraud_prediction": fraud_prediction,
                "business_rules": business_rules,
                "shap_values": shap_values,
            },
        )
