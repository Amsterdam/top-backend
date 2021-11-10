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
                    "sia_presedence",
                    "day_segments",
                    "week_segments",
                    "priorities",
                    "reasons",
                    "state_types",
                    "week_days",
                    "max_use_limit",
                    "start_time",
                )
            },
        ),
    )


@admin.register(TeamSettings)
class TeamSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "use_zaken_backend",
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
                    "use_zaken_backend",
                    "zaken_team_name",
                    "fraudprediction_pilot_enabled",
                    "fraud_prediction_model",
                    "show_issuemelding",
                )
            },
        ),
        (
            "Projects & stadia options",
            {
                "classes": ("collapse",),
                "fields": ("project_choices", "stadia_choices"),
            },
        ),
        (
            "Algoritm options",
            {
                "classes": ("collapse",),
                "fields": ("default_weights", "is_sia_weights", "top_cases_count"),
            },
        ),
        (
            "Visit options",
            {
                "classes": ("collapse",),
                "fields": ("observation_choices", "suggest_next_visit_choices"),
            },
        ),
        (
            "Visual options",
            {
                "classes": ("collapse",),
                "fields": ("marked_stadia", "show_vakantieverhuur"),
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
        "reason",
        "state_types",
        "priority",
        "primary_stadium",
        "secondary_stadium",
        "issuemelding",
        "is_sia",
    )
    list_editable = (
        "distance",
        "fraud_probability",
        "reason",
        "state_types",
        "priority",
        "primary_stadium",
        "secondary_stadium",
        "issuemelding",
        "is_sia",
    )
