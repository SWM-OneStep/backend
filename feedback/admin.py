from django.contrib import admin

from .models import Feedback


class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ["id", "user_id", "created_at"]
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
                    "is_completed",
                ]
            },
        ),
    ]


admin.site.register(Feedback, FeedbackAdmin)
