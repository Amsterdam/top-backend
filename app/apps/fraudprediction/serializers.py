from apps.fraudprediction.models import FraudPrediction
from rest_framework import serializers


class FraudPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudPrediction
        fields = (
            "fraud_prediction_model",
            "fraud_probability",
            "fraud_prediction",
            "business_rules",
            "shap_values",
            "sync_date",
        )
