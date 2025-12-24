import datetime
import uuid

from apps.users.utils import generate_username
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Meta:
        ordering = ["email"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        unique=True,
        blank=False,
        error_messages={
            "unique": "A user with that email already exists.",
        },
    )
    team_settings = models.ManyToManyField(
        to="planner.TeamSettings",
        blank=True,
        related_name="team_settings",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def get_current_itinerary(self):
        now = datetime.datetime.now()
        teams = self.teams.filter(
            itinerary__created_at__gte=datetime.datetime(now.year, now.month, now.day)
        )
        if teams:
            return teams[0].itinerary
        return None

    @property
    def current_itinerary_id(self):
        itinerary = self.get_current_itinerary
        return itinerary.id if itinerary else itinerary

    @property
    def current_team_settings_id(self):
        itinerary = self.get_current_itinerary
        return itinerary.settings.team_settings.id if itinerary else itinerary

    @property
    def full_name(self):
        """
        Parses name from email.
        a.van.de.boer -> A. Van De Boer
        anton -> Anton
        """

        if not self.email:
            return ""

        parts = self.email.split("@")[0].split(".")

        formatted_parts = []
        for part in parts:
            if len(part) == 1:
                formatted_parts.append(part.upper() + ".")
            else:
                formatted_parts.append(part.capitalize())

        return " ".join(formatted_parts)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.username = generate_username(self.email)
        super().save(*args, **kwargs)
