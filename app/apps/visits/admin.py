from datetime import timedelta

from apps.visits.models import (
    Observation,
    Situation,
    SuggestNextVisit,
    Visit,
    VisitMetaData,
)
from django.contrib import admin
from django.utils import timezone


class StartTimeFilter(admin.SimpleListFilter):
    title = "start_time"
    parameter_name = "start_time"

    def lookups(self, request, model_admin):
        return (
            ("today", "Today"),
            ("past_7_days", "Past 7 days"),
            ("this_month", "This month"),
            ("longer_than_a_month", "Longer than a month ago"),
        )

    def queryset(self, request, queryset):
        if self.value() == "today":
            today_start = timezone.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            today_end = today_start + timedelta(days=1)
            return queryset.filter(start_time__range=(today_start, today_end))

        elif self.value() == "past_7_days":
            past_7_days_start = timezone.now() - timedelta(days=7)
            return queryset.filter(start_time__gte=past_7_days_start)

        elif self.value() == "this_month":
            first_day_of_month = timezone.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            next_month = first_day_of_month.replace(month=first_day_of_month.month + 1)
            return queryset.filter(start_time__range=(first_day_of_month, next_month))

        elif self.value() == "longer_than_a_month":
            one_month_ago = timezone.now() - timedelta(days=30)
            return queryset.filter(start_time__lt=one_month_ago)

        return queryset


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "case_id",
        "author",
        "start_time",
        "completed",
        "situation",
    )
    search_fields = ("case_id__case_id",)
    list_filter = (StartTimeFilter, "completed")


@admin.register(VisitMetaData)
class VisitMetaData(admin.ModelAdmin):
    search_fields = ("visit__case_id__case_id",)
    list_display = ("visit", "date", "case_id")

    def date(self, obj):
        return obj.visit.start_time

    def case_id(self, obj):
        return obj.visit.case_id

    # def has_change_permission(self, request, obj=None):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

    # def has_add_permission(self, request):
    #     return False


@admin.register(Situation)
@admin.register(Observation)
@admin.register(SuggestNextVisit)
class ChoiceItemAdmin(admin.ModelAdmin):
    list_display = ("value", "position", "verbose")
    list_editable = ("position",)
    ordering = ("position",)
