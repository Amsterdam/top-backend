from apps.planner.models import (
    DaySettings,
    PostalCodeRange,
    PostalCodeRangeSet,
    TeamSettings,
    Weights,
)
from django.contrib import admin


class DaySettingsInline(admin.TabularInline):
    model = DaySettings
    extra = 0
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "housing_corporations",
                    "housing_corporation_combiteam",
                    "day_segments",
                    "week_segments",
                    "priorities",
                    "reasons",
                    "postal_code_ranges",
                    "districts",
                    "postal_code_ranges_presets",
                    "state_types",
                    "week_days",
                    "max_use_limit",
                    "start_time",
                    "project_ids",
                )
            },
        ),
    )


@admin.register(TeamSettings)
class TeamSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "fraudprediction_pilot_enabled",
        "enabled",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "enabled",
                    "zaken_team_id",
                    "fraudprediction_pilot_enabled",
                    "fraud_prediction_model",
                )
            },
        ),
        (
            "Algoritm options",
            {
                "classes": ("collapse",),
                "fields": ("default_weights", "top_cases_count"),
            },
        ),
        (
            "Visit options",
            {
                "classes": ("collapse",),
                "fields": ("observation_choices", "suggest_next_visit_choices"),
            },
        ),
    )
    inlines = [DaySettingsInline]


class PostalCodeRangeInline(admin.TabularInline):
    model = PostalCodeRange
    extra = 1


@admin.register(PostalCodeRangeSet)
class PostalCodeRangeSetAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [PostalCodeRangeInline]


@admin.register(Weights)
class WeightsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "distance",
        "fraud_probability",
        "priority",
    )
    list_editable = (
        "distance",
        "fraud_probability",
        "priority",
    )
