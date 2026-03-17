from apps.planner.models import (
    DaySettings,
    PostalCodeRange,
    PostalCodeRangeSet,
    TeamSettings,
    Weights,
)
from django.contrib import admin
from settings.const import WEEK_DAYS


class DaySettingsInline(admin.TabularInline):
    model = DaySettings
    extra = 0
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "week_days",
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
                    "max_use_limit",
                    "start_time",
                    "project_ids",
                    "subjects",
                    "tags",
                )
            },
        ),
    )


@admin.register(TeamSettings)
class TeamSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
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
        "priority",
    )
    list_editable = (
        "distance",
        "priority",
    )


@admin.register(DaySettings)
class DaySettingsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "week_days_display",
        "team_settings",
    )
    list_filter = ("team_settings",)

    def week_days_display(self, obj):
        indices = obj.week_days or []
        labels = []
        for idx in indices:
            try:
                labels.append(WEEK_DAYS[int(idx)])
            except (ValueError, TypeError, IndexError):
                labels.append(str(idx))
        return ", ".join(labels)

    week_days_display.short_description = "Week days"
