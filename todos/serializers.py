# todos/serializers.py
import re

import django.utils.timezone as timezone
from rest_framework import serializers

from accounts.models import User
from todos.utils import validate_lexo_order

from .models import Category, SubTodo, Todo, UserLastUsage


class PatchOrderSerializer(serializers.Serializer):
    prev_id = serializers.PrimaryKeyRelatedField(
        queryset=Todo.objects.all(), required=False, allow_null=True
    )
    next_id = serializers.PrimaryKeyRelatedField(
        queryset=Todo.objects.all(), required=False, allow_null=True
    )
    updated_order = serializers.CharField(max_length=255, required=True)


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
                data.get(field) for field in ["color", "title", "order"]
            ):
                raise serializers.ValidationError(
                    "At least one of color, title, order must be provided"
                )
            if data.get("user_id"):
                raise serializers.ValidationError("User cannot be updated")
            return data

        elif request.method == "POST":
            user_id = data.get("user_id")
            last_category = (
                Category.objects.filter(
                    user_id=user_id, deleted_at__isnull=True
                )
                .order_by("-order")
                .first()
            )
            if last_category is not None:
                last_order = last_category.order
                if (
                    validate_lexo_order(
                        prev=last_order, next=None, updated=data["order"]
                    )
                    is False
                ):
                    raise serializers.ValidationError("Order is invalid")
        return data


class SubTodoSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=255)
    todo = serializers.PrimaryKeyRelatedField(
        queryset=Todo.objects.all(), required=True
    )
    date = serializers.DateField(required=False, allow_null=True)
    order = serializers.CharField(max_length=255)
    is_completed = serializers.BooleanField(default=False)
    patch_order = PatchOrderSerializer(required=False)

    class Meta:
        model = SubTodo
        fields = "__all__"

    def validate_todo(self, data):
        try:
            Todo.objects.get(id=data.id)
        except Todo.DoesNotExist:
            raise serializers.ValidationError("Todo does not exist")
        return data

    def validate_patch_order(self, data):
        request = self.context["request"]
        if request.method == "PATCH":
            updated_order = data.get("updated_order")
            prev = data.get("prev_id").order if data.get("prev_id") else None
            next = data.get("next_id").order if data.get("next_id") else None
            if not validate_lexo_order(
                prev=prev, next=next, updated=updated_order
            ):
                raise serializers.ValidationError("Order is invalid")
        return data

    def validate(self, data):
        request = self.context["request"]
        if request.method == "PATCH":
            if not any(
                data.get(field)
                for field in ["content", "date", "is_completed", "order"]
            ):
                raise serializers.ValidationError(
                    "At least one of content, date, \
                        is_completed, order must be provided"
                )
            return data

        elif request.method == "POST":
            todo_id = data.get("todo").id
            last_subtodo = (
                SubTodo.objects.filter(
                    todo_id=todo_id, deleted_at__isnull=True
                )
                .order_by("-order")
                .first()
            )
            if last_subtodo is not None:
                last_order = last_subtodo.order
                if (
                    validate_lexo_order(
                        prev=last_order, next=None, updated=data["order"]
                    )
                    is False
                ):
                    raise serializers.ValidationError("Order is invalid")
        return data


class GetTodoSerializer(serializers.ModelSerializer):
    children = SubTodoSerializer(many=True, read_only=True, source="subtodos")

    class Meta:
        model = Todo
        fields = [
            "id",
            "content",
            "category_id",
            "start_date",
            "end_date",
            "user_id",
            "order",
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
    start_date = serializers.DateField(allow_null=True, required=False)
    end_date = serializers.DateField(allow_null=True, required=False)
    order = serializers.CharField(max_length=255)
    is_completed = serializers.BooleanField(default=False, required=False)
    patch_order = PatchOrderSerializer(required=False)

    class Meta:
        model = Todo
        fields = [
            "id",
            "content",
            "category_id",
            "start_date",
            "end_date",
            "user_id",
            "order",
            "is_completed",
            "patch_order",
        ]

    def validate_category_id(self, data):
        if not Category.objects.filter(id=data.id).exists():
            raise serializers.ValidationError("Category does not exist")
        return data

    def validate_user_id(self, data):
        if not User.objects.filter(id=data.id).exists():
            raise serializers.ValidationError("User does not exist")
        return data

    def validate_patch_order(self, data):
        request = self.context["request"]
        if request.method == "PATCH":
            updated_order = data.get("updated_order")
            prev = data.get("prev_id").order if data.get("prev_id") else None
            next = data.get("next_id").order if data.get("next_id") else None
            if not validate_lexo_order(
                prev=prev, next=next, updated=updated_order
            ):
                raise serializers.ValidationError("Order is invalid")
        return data

    def validate(self, data):
        request = self.context["request"]
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                "Start date should be less than end date"
            )

        if request.method == "PATCH":
            if not any(
                data.get(field)
                for field in [
                    "content",
                    "category_id",
                    "start_date",
                    "end_date",
                    "is_completed",
                    "order",
                ]
            ):
                raise serializers.ValidationError(
                    "At least one of content, category_id, start_date, end_date, is_completed must be provided"  # noqa : E501
                )
            if data.get("user_id"):
                raise serializers.ValidationError("User cannot be updated")
        elif request.method == "POST":
            user_id = data.get("user_id")
            last_todo = (
                Todo.objects.filter(user_id=user_id, deleted_at__isnull=True)
                .order_by("-order")
                .first()
            )
            if last_todo and not validate_lexo_order(
                prev=last_todo.order, next=None, updated=data["order"]
            ):
                raise serializers.ValidationError("Order is invalid")

        return data

    def update(self, instance, validated_data):
        # Update the fields as usual
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Set the updated_at field to the current time
        instance.updated_at = timezone.now()
        instance.save()
        return instance


class UserLastUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLastUsage
        fields = ["user_id", "last_used_at"]
