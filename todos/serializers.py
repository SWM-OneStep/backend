# todos/serializers.py
import re

import django.utils.timezone as timezone
from rest_framework import serializers

from accounts.models import User

from .models import Category, SubTodo, Todo


class PatchRankSerializer(serializers.Serializer):
    prev_id = serializers.PrimaryKeyRelatedField(
        queryset=Todo.objects.all(), required=False, allow_null=True
    )
    next_id = serializers.PrimaryKeyRelatedField(
        queryset=Todo.objects.all(), required=False, allow_null=True
    )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

    def validate_user_id(self, data):
        try:
            User.objects.get(id=data.id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        return data

    def validate_color(self, data):
        hex_color_pattern = r"^#([A-Fa-f0-9]{6})$"
        match = re.match(hex_color_pattern, data)
        if bool(match) is False:
            raise serializers.ValidationError("Color code is invalid")
        return data

    def validate(self, data):
        request = self.context["request"]
        if request.method == "PATCH":
            if not any(
                data.get(field) for field in ["color", "title", "rank"]
            ):
                raise serializers.ValidationError(
                    "At least one of color, title, rank must be provided"
                )
            if data.get("user_id"):
                raise serializers.ValidationError("User cannot be updated")
        return data


class SubTodoSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=255)
    todo_id = serializers.PrimaryKeyRelatedField(
        queryset=Todo.objects.all(), required=True
    )
    date = serializers.DateField(required=False, allow_null=True)
    rank = serializers.CharField(max_length=255, required=False)
    is_completed = serializers.BooleanField(default=False)
    patch_rank = PatchRankSerializer(required=False)

    class Meta:
        model = SubTodo
        fields = "__all__"

    def validate_todo(self, data):
        try:
            Todo.objects.get(id=data.id)
        except Todo.DoesNotExist:
            raise serializers.ValidationError("Todo does not exist")
        return data

    def validate(self, data):
        request = self.context["request"]
        if request.method == "PATCH":
            if not any(
                data.get(field)
                for field in ["content", "date", "is_completed", "patch_rank"]
            ):
                raise serializers.ValidationError(
                    "At least one of content, date, \
                        is_completed, rank must be provided"
                )
            return data
        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == "patch_rank":
                SubTodo.objects.update_rank(
                    instance, value.get("prev_id"), value.get("next_id")
                )
            else:
                setattr(instance, attr, value)
        instance.updated_at = timezone.now()
        instance.save()
        return instance


class GetTodoSerializer(serializers.ModelSerializer):
    children = SubTodoSerializer(many=True, read_only=True, source="subtodos")

    class Meta:
        model = Todo
        fields = [
            "id",
            "content",
            "category_id",
            "date",
            "due_time",
            "user_id",
            "rank",
            "is_completed",
            "children",
        ]


class TodoSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=255)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=True
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=True
    )
    date = serializers.DateField(allow_null=True, required=False)
    due_time = serializers.TimeField(allow_null=True, required=False)
    rank = serializers.CharField(max_length=255, required=False)
    is_completed = serializers.BooleanField(default=False, required=False)
    patch_rank = PatchRankSerializer(required=False)

    class Meta:
        model = Todo
        fields = [
            "id",
            "content",
            "category_id",
            "date",
            "due_time",
            "user_id",
            "rank",
            "is_completed",
            "patch_rank",
        ]

    def validate_category_id(self, data):
        if not Category.objects.filter(id=data.id).exists():
            raise serializers.ValidationError("Category does not exist")
        return data

    def validate_user_id(self, data):
        if not User.objects.filter(id=data.id).exists():
            raise serializers.ValidationError("User does not exist")
        return data

    def validate(self, data):
        request = self.context["request"]

        if request.method == "PATCH":
            if not any(
                data.get(field)
                for field in [
                    "content",
                    "category_id",
                    "date",
                    "is_completed",
                    "patch_rank",
                ]
            ):
                raise serializers.ValidationError(
                    "At least one of content, category_id, date, is_completed must be provided"  # noqa : E501
                )
            if data.get("user_id"):
                raise serializers.ValidationError("User cannot be updated")
        return data

    def update(self, instance, validated_data):
        # Update the fields as usual
        for attr, value in validated_data.items():
            if attr == "patch_rank":
                # If the rank field is provided, update the rank field
                Todo.objects.update_rank(
                    instance, value.get("prev_id"), value.get("next_id")
                )
            else:
                setattr(instance, attr, value)

        # Set the updated_at field to the current time
        instance.updated_at = timezone.now()
        instance.save()
        return instance
