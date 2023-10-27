from apps.cases.models import Case
from apps.fraudprediction.models import FraudPrediction
from apps.users.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Visit(models.Model):
    """Captures data of a visit"""

    situation = models.CharField(max_length=50, null=True, blank=True)
    observations = ArrayField(models.CharField(max_length=50), blank=True, null=True)
    case_id = models.ForeignKey(
        Case, on_delete=models.CASCADE, related_name="case_visits"
    )
    itinerary_item = models.ForeignKey(
        "itinerary.ItineraryItem",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="visits",
    )
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=False)

    description = models.TextField(
        null=True
    )  # these are the notes when access was granted

    # Describe if next visit can go ahead and why yes or no
    can_next_visit_go_ahead = models.BooleanField(default=True, blank=True, null=True)
    can_next_visit_go_ahead_description = models.TextField(null=True, default=None)

    # suggest_visit_next_time = models.BooleanField(default=True) # TODO not sure about this one
    suggest_next_visit = models.CharField(null=True, max_length=50)
    suggest_next_visit_description = models.TextField(
        null=True, blank=True, default=None
    )

    # personal notes to help make report at the office/as reminders for TH.
    personal_notes = models.TextField(blank=True, null=True, default=None)
    completed = models.BooleanField(default=True)

    def get_observation_string(self):
        return (
            Situation.objects.filter(value=self.situation)[0].verbose
            if Situation.objects.filter(value=self.situation)
            else ""
        )

    def get_parameters(self):
        observations = self.observations if self.observations else []
        return ", ".join(
            [
                Observation.objects.filter(value=o)[0].verbose
                for o in observations
                if Observation.objects.filter(value=o)
            ]
        )

    def capture_visit_meta_data(self):
        """Captures visit data"""
        visit_meta_data = VisitMetaData.objects.get_or_create(visit=self)[0]

        try:
            fraud_prediction = self.itinerary_item.case.fraud_prediction
        except FraudPrediction.DoesNotExist:
            return

        # Add visit data to persist it as judicial documentation
        visit_meta_data.fraud_probability = fraud_prediction.fraud_probability
        visit_meta_data.fraud_prediction_business_rules = (
            fraud_prediction.business_rules
        )
        visit_meta_data.fraud_prediction_shap_values = fraud_prediction.shap_values
        visit_meta_data.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.itinerary_item and self.itinerary_item.itinerary:
            self.team_members.all().delete()
            for u in self.itinerary_item.itinerary.team_members.all():
                member = VisitTeamMember(visit=self, user=u.user)
                member.save()


class VisitTeamMember(models.Model):
    """Member of an Visit Team"""

    class Meta:
        unique_together = ["user", "visit"]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, related_name="visit_team_members"
    )

    visit = models.ForeignKey(
        Visit, on_delete=models.CASCADE, null=False, related_name="team_members"
    )

    def __str__(self):
        return self.user.full_name


class VisitMetaData(models.Model):
    """
    Some data surrounding a visit is transient, and can change over time.
    One example are the fraud predictions, which change over the lifetime of a case.
    This model serves to capture and persist (meta) data at the time of a visit.
    The data should be relevant as (legal) documentation.
    """

    visit = models.OneToOneField(
        to=Visit, on_delete=models.CASCADE, related_name="meta_data", unique=True
    )

    # Persist the fraud prediction data here
    fraud_probability = models.FloatField(null=True)
    fraud_prediction_business_rules = models.JSONField(null=True)
    fraud_prediction_shap_values = models.JSONField(null=True)

    # Expand with more meta data later (for example, planner settings)


class ChoiceItem(models.Model):
    value = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
    )
    verbose = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=False,
    )
    position = models.FloatField(null=False, blank=False)

    def __str__(self):
        return self.value

    class Meta:
        abstract = True


class Situation(ChoiceItem):
    class Meta:
        abstract = False
        ordering = ("position",)


class Observation(ChoiceItem):
    class Meta:
        abstract = False
        ordering = ("position",)


class SuggestNextVisit(ChoiceItem):
    class Meta:
        abstract = False
        ordering = ("position",)
