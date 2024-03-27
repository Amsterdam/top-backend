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


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_filter = (HasUnderscoreFilter, "is_top_bwv_case")
    list_display = ("id", "case_id", "is_top_bwv_case")
    search_fields = ("case_id",)


class RedisKeyAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('redis-keys/', self.show_redis_keys),
        ]
        return custom_urls + urls

    def show_redis_keys(self, request):
        redis_connection = get_redis_connection()
        keys = redis_connection.keys('*')  # Change the pattern according to your needs
        key_list = [key.decode('utf-8') for key in keys]
        content = '\n'.join(key_list)
        return HttpResponse(content, content_type='text/plain')

admin.site.register(RedisKeyAdmin)