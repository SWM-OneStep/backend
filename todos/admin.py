# Register your models here.
from django.contrib import admin

from .models import Category, SubTodo, Todo


class TodoAdmin(admin.ModelAdmin):
    readonly_fields = ["id"]
    list_display = [
        "id",
        "content",
        "user_id",
        "category_id",
        "order",
        "due_time",
        "date",
        "is_completed",
    ]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "id",
                    "content",
                    "user_id",
                    "category_id",
                    "order",
                    "due_time",
                    "is_completed",
                ]
            },
        ),
        (
            "Date information",
            {"fields": ["date"], "classes": ["collapse"]},
        ),
    ]


class SubTodoAdmin(admin.ModelAdmin):
    readonly_fields = ["id"]
    list_display = [
        "id",
        "content",
        "todo",
        "due_time",
        "order",
        "is_completed",
    ]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "id",
                    "content",
                    "todo",
                    "due_time",
                    "order",
                    "is_completed",
                ]
            },
        ),
        (
            "Date information",
            {"fields": ["date"], "classes": ["collapse"]},
        ),
    ]


class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ["id"]
    list_display = ["id", "title", "user_id", "color", "order"]
    fieldsets = [
        (
            None,
            {"fields": ["id", "title", "user_id", "color", "order"]},
        ),
    ]


admin.site.register(Todo, TodoAdmin)
admin.site.register(SubTodo, SubTodoAdmin)
admin.site.register(Category, CategoryAdmin)
