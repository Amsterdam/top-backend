from datetime import timedelta

from apps.itinerary.models import (
    Itinerary,
    ItineraryItem,
    ItinerarySettings,
    ItineraryTeamMember,
    Note,
    PostalCodeSettings,
)
from apps.itinerary.serializers import ItinerarySerializer
from django.contrib import admin
from django.db.models import Prefetch
from django.http import JsonResponse
from django.utils import timezone


class PostalCodeSettingsInline(admin.StackedInline):
    fields = ("range_start", "range_end")
    model = PostalCodeSettings


class ItinerarySettingsInline(admin.StackedInline):
    fields = (
        "opening_date",
        "day_settings",
        "target_length",
        "start_case",
    )
    model = ItinerarySettings
    raw_id_fields = ("day_settings",)
    autocomplete_fields = ("start_case",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("itinerary", "day_settings", "start_case")
        )


class ItineraryTeamMemberInline(admin.StackedInline):
    fields = ("user",)
    model = ItineraryTeamMember
    extra = 0
    autocomplete_fields = ("user",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


class ItineraryItemInline(admin.StackedInline):
    fields = ("case",)
    model = ItineraryItem
    extra = 0
    autocomplete_fields = ("case",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("case")


class CreatedAtFilter(admin.SimpleListFilter):
    title = "created_at"
    parameter_name = "created_at"

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
            return queryset.filter(created_at__range=(today_start, today_end))

        elif self.value() == "past_7_days":
            past_7_days_start = timezone.now() - timedelta(days=7)
            return queryset.filter(created_at__gte=past_7_days_start)

        elif self.value() == "this_month":
            first_day_of_month = timezone.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            next_month = first_day_of_month.replace(month=first_day_of_month.month + 1)
            return queryset.filter(created_at__range=(first_day_of_month, next_month))

        elif self.value() == "longer_than_a_month":
            one_month_ago = timezone.now() - timedelta(days=30)
            return queryset.filter(created_at__lt=one_month_ago)

        return queryset


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "created_at",
        "start_case",
    )
    search_fields = ["team_members__user__email"]
    list_filter = (CreatedAtFilter,)

    inlines = [
        ItineraryTeamMemberInline,
        ItineraryItemInline,
        ItinerarySettingsInline,
        PostalCodeSettingsInline,
    ]

    actions = ["export_as_json"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("settings__start_case").prefetch_related(
            Prefetch(
                "team_members",
                queryset=ItineraryTeamMember.objects.select_related("user"),
            )
        )

    def start_case(self, obj):
        return obj.settings.start_case

    def export_as_json(self, request, queryset):
        serializer = ItinerarySerializer(queryset.all(), many=True)
        return JsonResponse({"looplijsten": serializer.data})


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    fields = ("itinerary_item", "text", "author")


@admin.register(ItineraryItem)
class ItineraryItemAdmin(admin.ModelAdmin):
    fields = (
        "itinerary",
        "case",
        "position",
        "external_state_id",
    )
    list_display = (
        "case",
        "itinerary",
    )
    search_fields = ["case__case_id"]
