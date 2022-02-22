import datetime

import requests
from apps.cases.models import Project, Stadium, StadiumLabel
from apps.visits.models import Observation, Situation, SuggestNextVisit
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from settings.const import POSTAL_CODE_RANGES, WEEK_DAYS_CHOICES
from utils.queries_zaken_api import get_headers

from .const import SCORING_WEIGHTS
from .mock import get_team_reasons, get_team_schedules, get_team_state_types

WEIGHTS_VALIDATORS = [MinValueValidator(0), MaxValueValidator(1)]

FRAUD_PREDICTION_MODEL_CHOICES = [[m, m] for m in settings.FRAUD_PREDICTION_MODELS]


def team_settings_settings_default():
    # TODO: remove this unused so fix in migrations
    return {}


def day_settings__postal_code_ranges__default():
    return POSTAL_CODE_RANGES


class TeamSettings(models.Model):
    name = models.CharField(
        max_length=100,
    )
    enabled = models.BooleanField(
        default=True,
    )
    use_zaken_backend = models.BooleanField(
        default=False,
    )
    zaken_team_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    fraudprediction_pilot_enabled = models.BooleanField(
        default=False,
        help_text="enables fraudprediction A/B testing for this theme on AZA cases",
    )
    default_weights = models.ForeignKey(
        to="Weights",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="team_settings_default_weights",
    )
    is_sia_weights = models.ForeignKey(
        to="Weights",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="team_settings_is_sia_weights",
    )
    show_issuemelding = models.BooleanField(
        default=True,
    )
    show_vakantieverhuur = models.BooleanField(
        default=True,
    )
    project_choices = models.ManyToManyField(
        to=Project,
        blank=True,
        related_name="team_settings_list",
    )
    stadia_choices = models.ManyToManyField(
        to=Stadium,
        blank=True,
        related_name="team_settings_list",
    )
    fraud_prediction_model = models.CharField(
        choices=FRAUD_PREDICTION_MODEL_CHOICES,
        max_length=50,
        blank=True,
        null=True,
    )
    marked_stadia = models.ManyToManyField(
        to=StadiumLabel,
        blank=True,
        related_name="stadium_label_team_settings_list",
    )
    observation_choices = models.ManyToManyField(
        to=Observation,
        blank=True,
        related_name="team_settings_list",
    )
    suggest_next_visit_choices = models.ManyToManyField(
        to=SuggestNextVisit,
        blank=True,
        related_name="team_settings_list",
    )
    top_cases_count = models.PositiveSmallIntegerField(
        help_text="Dit getal bepaald hoeveel van best matches zaken, gebruikt moeten worden als start punt. Als hier 0 gebruikt wordt, worden alle gevonden zaken gebruikt als start punt. Dit betekent dat 0 de langzaamste optie is voor het genereren van een looplijst.",
        default=0,
    )

    def fetch_team_schedules(self, auth_header=None):
        if settings.USE_ZAKEN_MOCK_DATA:
            return get_team_schedules()

        url = f"{settings.ZAKEN_API_URL}/themes/{self.zaken_team_name}/schedule-types/"

        response = requests.get(
            url,
            timeout=5,
            headers=get_headers(auth_header),
        )
        response.raise_for_status()

        return response.json()

    def fetch_team_reasons(self, auth_header=None):
        if settings.USE_ZAKEN_MOCK_DATA:
            return get_team_reasons()

        url = f"{settings.ZAKEN_API_URL}/themes/{self.zaken_team_name}/reasons/"

        response = requests.get(
            url,
            timeout=5,
            headers=get_headers(auth_header),
        )
        response.raise_for_status()

        return response.json().get("results", [])

    class Meta:
        verbose_name_plural = "Team settings"
        ordering = ["name"]

    @property
    def situation_choices(self):
        return list(Situation.objects.all().values_list("value", flat=True))

    def __str__(self):
        return self.name


class PostalCodeRangeSet(models.Model):
    name = models.CharField(
        max_length=50,
    )

    class Meta:
        ordering = ["name"]


class PostalCodeRange(models.Model):
    range_start = models.PositiveSmallIntegerField(
        default=1000, validators=[MaxValueValidator(9999), MinValueValidator(1000)]
    )
    range_end = models.PositiveSmallIntegerField(
        default=1000, validators=[MaxValueValidator(9999), MinValueValidator(1000)]
    )
    postal_code_range_set = models.ForeignKey(
        to=PostalCodeRangeSet,
        on_delete=models.CASCADE,
        related_name="postal_code_ranges",
    )

    def save(self, *args, **kwargs):
        if not self.range_end or self.range_end < self.range_start:
            self.range_end = self.range_start
        super().save(*args, **kwargs)


class DaySettings(models.Model):
    team_settings = models.ForeignKey(
        to=TeamSettings, related_name="day_settings_list", on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=50,
    )
    week_day = models.PositiveSmallIntegerField(
        choices=WEEK_DAYS_CHOICES,
        blank=True,
        null=True,
    )
    week_days = ArrayField(
        base_field=models.PositiveSmallIntegerField(),
        blank=True,
        null=True,
    )
    start_time = models.TimeField(
        blank=True,
        null=True,
    )
    opening_date = models.DateField(
        default="2019-01-01",
    )
    postal_code_ranges = models.JSONField(
        default=day_settings__postal_code_ranges__default,
    )
    postal_code_ranges_presets = models.ManyToManyField(
        to=PostalCodeRangeSet,
        blank=True,
        related_name="postal_code_ranges_presets_day_settings_list",
    )
    length_of_list = models.PositiveSmallIntegerField(
        default=8,
    )
    max_use_limit = models.PositiveSmallIntegerField(default=0)

    # AZA Fields
    day_segments = ArrayField(
        base_field=models.PositiveSmallIntegerField(),
        blank=True,
        null=True,
    )
    week_segments = ArrayField(
        base_field=models.PositiveSmallIntegerField(),
        blank=True,
        null=True,
    )
    priorities = ArrayField(
        base_field=models.PositiveSmallIntegerField(),
        blank=True,
        null=True,
    )
    reasons = ArrayField(
        base_field=models.PositiveSmallIntegerField(),
        blank=True,
        null=True,
    )
    state_types = ArrayField(
        base_field=models.PositiveSmallIntegerField(),
        blank=True,
        null=True,
    )

    # BWV Fields
    projects = models.ManyToManyField(
        to=Project,
        blank=True,
        related_name="projects_day_settings_list",
    )
    primary_stadium = models.ForeignKey(
        to=Stadium,
        null=True,
        blank=True,
        related_name="primary_stadium_day_settings_list",
        on_delete=models.SET_NULL,
    )
    secondary_stadia = models.ManyToManyField(
        to=Stadium,
        blank=True,
        related_name="secondary_stadia_day_settings_list",
    )
    exclude_stadia = models.ManyToManyField(
        to=Stadium,
        blank=True,
        related_name="exclude_stadia_day_settings_list",
    )
    sia_presedence = models.BooleanField(default=False)

    def fetch_team_schedules(self, auth_header=None):
        url = f"{settings.ZAKEN_API_URL}/themes/{self.team_settings.zaken_team_name}/schedule-types/"

        response = requests.get(
            url,
            timeout=5,
            headers=get_headers(auth_header),
        )
        response.raise_for_status()

        return response.json()

    def fetch_team_reasons(self, auth_header=None):
        url = f"{settings.ZAKEN_API_URL}/themes/{self.team_settings.zaken_team_name}/reasons/"

        response = requests.get(
            url,
            timeout=5,
            headers=get_headers(auth_header),
        )
        response.raise_for_status()

        return response.json().get("results", [])

    @property
    def used_today_count(self):
        from apps.itinerary.models import Itinerary

        date = datetime.datetime.now()
        return Itinerary.objects.filter(
            created_at=date,
            settings__day_settings=self,
        ).count()

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Day settings"

    def __str__(self):
        return "%s - %s" % (
            self.team_settings.name,
            self.name,
        )


class Weights(models.Model):
    name = models.CharField(
        max_length=50,
    )
    distance = models.FloatField(
        default=SCORING_WEIGHTS.DISTANCE.value,
        validators=WEIGHTS_VALIDATORS,
    )
    fraud_probability = models.FloatField(
        default=SCORING_WEIGHTS.FRAUD_PROBABILITY.value,
        validators=WEIGHTS_VALIDATORS,
    )
    reason = models.FloatField(
        default=SCORING_WEIGHTS.REASON.value,
        validators=WEIGHTS_VALIDATORS,
    )
    state_types = models.FloatField(
        default=SCORING_WEIGHTS.STATE_TYPE.value,
        validators=WEIGHTS_VALIDATORS,
    )
    priority = models.FloatField(
        default=SCORING_WEIGHTS.PRIORITY.value,
        validators=WEIGHTS_VALIDATORS,
    )
    primary_stadium = models.FloatField(
        default=SCORING_WEIGHTS.PRIMARY_STADIUM.value,
        validators=WEIGHTS_VALIDATORS,
    )
    secondary_stadium = models.FloatField(
        default=SCORING_WEIGHTS.SECONDARY_STADIUM.value,
        validators=WEIGHTS_VALIDATORS,
    )
    issuemelding = models.FloatField(
        default=SCORING_WEIGHTS.ISSUEMELDING.value,
        validators=WEIGHTS_VALIDATORS,
    )
    is_sia = models.FloatField(
        default=SCORING_WEIGHTS.IS_SIA.value,
        validators=WEIGHTS_VALIDATORS,
    )

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Weights"

    def score(
        self,
        distance,
        fraud_probability,
        reason,
        state_types,
        priority,
        primary_stadium,
        secondary_stadium,
        issuemelding,
        is_sia,
    ):
        values = [
            distance,
            fraud_probability,
            reason,
            state_types,
            priority,
            primary_stadium,
            secondary_stadium,
            issuemelding,
            is_sia,
        ]
        weights = [
            self.distance,
            self.fraud_probability,
            self.reason,
            self.state_types,
            self.priority,
            self.primary_stadium,
            self.secondary_stadium,
            self.issuemelding,
            self.is_sia,
        ]

        products = [value * weight for value, weight in zip(values, weights)]
        return sum(products)

    def __str__(self):
        return "%s: %s-%s-%s-%s-%s-%s-%s-%s-%s" % (
            self.name,
            self.distance,
            self.fraud_probability,
            self.reason,
            self.state_types,
            self.priority,
            self.primary_stadium,
            self.secondary_stadium,
            self.issuemelding,
            self.is_sia,
        )
