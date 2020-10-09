import datetime

from apps.fraudprediction.models import FraudPrediction
from django.db import models
from settings.const import PROJECTS, STADIA
from utils.queries import get_case


class Case(models.Model):
    class Meta:
        ordering = ["case_id"]

    """
    A simple case model
    """
    case_id = models.CharField(max_length=255, null=True, blank=False)

    def get(case_id):
        return Case.objects.get_or_create(case_id=case_id)[0]

    def __get_case__(self, case_id):
        return get_case(case_id)

    def get_location(self):
        case_data = self.__get_case__(self.case_id)
        return {"lat": case_data.get("lat"), "lng": case_data.get("lng")}

    @property
    def bwv_data(self):
        return self.__get_case__(self.case_id)

    @property
    def itinerary(self):
        now = datetime.datetime.now()
        itinerary_items = self.cases.filter(
            itinerary__created_at__gte=datetime.datetime(now.year, now.month, now.day)
        )
        if itinerary_items:
            return itinerary_items[0].itinerary
        return None

    @property
    def team_settings(self):
        return self.itinerary.settings.team_settings if self.itinerary else None

    @property
    def fraud_prediction(self):
        fraud_prediction = FraudPrediction.objects.get(case_id=self.case_id)
        return fraud_prediction

    def __str__(self):
        if self.case_id:
            return self.case_id
        return ""


class Project(models.Model):
    CHOICES = [(project, project) for project in PROJECTS]

    name = models.CharField(
        max_length=255, null=False, blank=False, unique=True, choices=CHOICES
    )

    def get(name):
        return Project.objects.get_or_create(name=name)[0]

    def __str__(self):
        return self.name


class Stadium(models.Model):
    CHOICES = [(stadium, stadium) for stadium in STADIA]

    name = models.CharField(
        max_length=255, null=False, blank=False, unique=True, choices=CHOICES
    )

    def get(name):
        return Stadium.objects.get_or_create(name=name)[0]

    def __str__(self):
        return self.name
