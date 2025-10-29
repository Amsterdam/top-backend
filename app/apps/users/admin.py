from apps.users.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (
            "None",
            {"fields": ("email", "password", "username", "first_name", "last_name")},
        ),
        (
            "None",
            {"fields": ("team_settings",)},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = ("full_name", "email", "is_staff", "last_login", "date_joined")
    search_fields = ("email",)
    ordering = ("email",)
    readonly_fields = (
        "date_joined",
        "last_login",
        "username",
        "first_name",
        "last_name",
    )
