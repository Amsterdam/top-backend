from apps.cases.models import Case
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django_redis import get_redis_connection

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
