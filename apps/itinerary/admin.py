from django.contrib import admin
from .models import Itinerary, ItineraryItem

class ItineraryItemInline(admin.StackedInline):
    model = ItineraryItem
    readonly_fields = ('case_id', 'address', 'postal_code_area', 'postal_code_street')
    can_delete = False
    extra = 0

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ('__str__',)

    inlines = [
        ItineraryItemInline,
    ]
