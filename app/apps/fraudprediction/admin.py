from apps.fraudprediction.models import FraudPrediction
from django.contrib import admin


@admin.register(FraudPrediction)
class FraudPredictionAdmin(admin.ModelAdmin):
    list_display = (
        "case_id",
        "business_rules",
        "fraud_prediction",
        "fraud_probability",
        "sync_date",
        "fraud_prediction_model",
    )
    list_filter = (
        "fraud_prediction_model",
        "sync_date",
        "fraud_prediction",
    )

    search_fields = ("case_id",)

    # fields = (
    #     "case_id",
    #     "fraud_prediction_model",
    #     "fraud_probability",
    #     "fraud_prediction",
    #     "business_rules",
    #     "shap_values",
    #     "sync_date",
    # )

    # readonly_fields = fields
