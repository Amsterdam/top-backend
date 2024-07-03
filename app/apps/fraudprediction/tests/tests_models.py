from datetime import datetime

from apps.fraudprediction.models import FraudPrediction
from django.test import TestCase
from freezegun import freeze_time
from pytz import UTC


class FraudPredictionModelTest(TestCase):
    CASE_ID = "FOO_CASE_ID"

    def get_and_create(self):
        return FraudPrediction.objects.create(
            case_id=self.CASE_ID,
            fraud_probability=0.8,
            fraud_prediction=True,
            business_rules={},
            shap_values={},
        )

    def test_create_fraud_prediction(self):
        """
        A FraudPrediction can be created
        """
        self.assertEqual(FraudPrediction.objects.count(), 0)
        self.get_and_create()
        self.assertEqual(FraudPrediction.objects.count(), 1)

    def test_fraud_prediction_string_representation(self):
        fraud_prediction = self.get_and_create()
        self.assertEqual(self.CASE_ID, str(fraud_prediction))

    @freeze_time("2019-12-25")
    def test_fraud_prediction_sync_date(self):
        """
        The sync date should be the current date
        """
        fraud_prediction = self.get_and_create()
        self.assertEquals(
            fraud_prediction.sync_date, datetime(2019, 12, 25, tzinfo=UTC)
        )
