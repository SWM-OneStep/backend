from django.contrib import admin

from .models import Feedback


class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ["id", "user_id", "created_at"]
    list_display = [
        "id",
        "user_id",
        "title",
        "category",
        "status",
        "created_at",
    ]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "id",
                    "user_id",
                    "title",
                    "category",
                    "description",
                    "created_at",
                    "status",
                ]
            },
        ),
    ]


admin.site.register(Feedback, FeedbackAdmin)
