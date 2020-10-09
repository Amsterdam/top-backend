from django.db import models
from settings.const import EXAMPLE_PLANNER_SETTINGS

from .const import TEAM_TYPE_CHOICES, TEAM_TYPE_VAKANTIEVERHUUR


class TeamSettings(models.Model):
    name = models.CharField(max_length=100,)
    team_type = models.CharField(
        max_length=100, choices=TEAM_TYPE_CHOICES, default=TEAM_TYPE_VAKANTIEVERHUUR
    )
    settings = models.JSONField(default=EXAMPLE_PLANNER_SETTINGS,)

    def __str__(self):
        return self.name
