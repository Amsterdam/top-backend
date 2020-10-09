from apps.planner.models import TeamSettings
from django.contrib import admin


@admin.register(TeamSettings)
class TeamSettingsAdmin(admin.ModelAdmin):
    list_display = ("name",)
