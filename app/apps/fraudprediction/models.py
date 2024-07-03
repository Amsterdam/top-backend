from django.conf import settings
from django.db import models

FRAUD_PREDICTION_MODEL_CHOICES = [[m, m] for m in settings.FRAUD_PREDICTION_MODELS]


class FraudPrediction(models.Model):
    """
    A case fraud prediction
    """

    case_id = models.CharField(max_length=255, null=True, blank=False, unique=True)
    fraud_prediction_model = models.CharField(
        choices=FRAUD_PREDICTION_MODEL_CHOICES,
        max_length=50,
        blank=True,
        null=True,
    )
    fraud_probability = models.FloatField(null=False)
    fraud_prediction = models.BooleanField(null=False)
    business_rules = models.JSONField(null=False)
    shap_values = models.JSONField(null=False)
    sync_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.case_id
