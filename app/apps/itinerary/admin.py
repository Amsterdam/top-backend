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
from django.http import JsonResponse


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


class ItineraryTeamMemberInline(admin.StackedInline):
    fields = ("user",)
    model = ItineraryTeamMember
    extra = 0


class ItineraryItemInline(admin.StackedInline):
    fields = ("case",)
    model = ItineraryItem
    extra = 0


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "created_at",
        "start_case",
    )

    inlines = [
        ItineraryTeamMemberInline,
        ItineraryItemInline,
        ItinerarySettingsInline,
        PostalCodeSettingsInline,
    ]

    actions = ["export_as_json"]

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
