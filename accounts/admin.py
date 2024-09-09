# Register your models here.
from django.contrib import admin

from .models import Device, User


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ["id"]
    list_display = [
        "id",
        "email",
        "username",
        "is_active",
        "is_staff",
        "is_superuser",
    ]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "id",
                    "email",
                    "username",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ]
            },
        ),
    ]


class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ["id", "created_at"]
    list_display = ["id", "user_id", "created_at", "deleted_at"]
    fieldsets = [
        (
            None,
            {"fields": ["id", "user_id", "created_at", "deleted_at"]},
        ),
    ]


admin.site.register(User, UserAdmin)
admin.site.register(Device, DeviceAdmin)
