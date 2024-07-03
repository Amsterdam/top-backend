from apps.cases.models import Case
from django.contrib import admin
from django.contrib.admin import SimpleListFilter


class HasUnderscoreFilter(SimpleListFilter):
    title = "underscore"
    parameter_name = "case_id"

    def lookups(self, request, model_admin):
        return [
            ("no_", "Contains no underscore"),
            ("yes_", "Contains underscore"),
        ]

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == "no_":
                return queryset.all().exclude(case_id__contains="_")
            elif self.value() == "yes_":
                return queryset.all().filter(case_id__contains="_")


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_filter = (HasUnderscoreFilter, "is_top_bwv_case")
    list_display = ("id", "case_id", "is_top_bwv_case")
    search_fields = ("case_id",)
