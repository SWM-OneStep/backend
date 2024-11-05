# Register your models here.
from django.contrib import admin

from .models import Device, PatchNote, User


class UserAdmin(admin.ModelAdmin):
    readonly_fields = [
        "id",
        "social_provider",
        "username",
        "created_at",
        "updated_at",
    ]
    list_display = [
        "id",
        "username",
        "social_provider",
        "created_at",
        "deleted_at",
        "updated_at",
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
                    "username",
                    "social_provider",
                    "created_at",
                    "deleted_at",
                    "updated_at",
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


class PatchNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")


admin.site.register(User, UserAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(PatchNote, PatchNoteAdmin)
