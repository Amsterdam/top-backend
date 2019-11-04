from django.contrib import admin
from .models import Itinerary, ItineraryItem

class ItineraryItemInline(admin.TabularInline):
    model = ItineraryItem
    fields = ('case_id', 'address', 'postal_code_area', 'postal_code_street')

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ('__str__',)

    inlines = [
        ItineraryItemInline,
    ]

@admin.register(ItineraryItem)
class ItineraryItemAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
