# todos/serializers.py
from rest_framework import serializers

from .models import Category, SubTodo, Todo


class SwaggerTodoSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=255)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=True
    )
    date = serializers.DateField(allow_null=True, required=False)
    due_time = serializers.TimeField(allow_null=True, required=False)
    is_completed = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = Todo
        fields = [
            "id",
            "content",
            "category_id",
            "date",
            "due_time",
            "user_id",
            "is_completed",
            "rank",
        ]
        read_only_fields = ["user_id", "rank", "id"]


class SwaggerSubTodoSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=255)
    todo_id = serializers.PrimaryKeyRelatedField(
        queryset=Todo.objects.all(), required=True
    )
    date = serializers.DateField(required=False, allow_null=True)
    due_time = serializers.TimeField(required=False, allow_null=True)
    is_completed = serializers.BooleanField(default=False)

    class Meta:
        model = Todo
        fields = [
            "id",
            "todo_id",
            "content",
            "date",
            "due_time",
            "is_completed",
            "rank",
        ]
        read_only_fields = ["rank", "id"]


class SwaggerCategorySerializer(serializers.ModelSerializer):
    color = serializers.IntegerField(min_value=0, max_value=8)
    title = serializers.CharField(max_length=100)

    class Meta:
        model = Category
        fields = ["id", "user_id", "color", "title", "rank"]
        read_only_fields = ["rank", "id", "user_id"]


class SwaggerRankSerializer(serializers.ModelSerializer):
    prev_id = serializers.IntegerField()
    next_id = serializers.IntegerField()

    class Meta:
        model = Todo
        fields = ["prev_id", "next_id"]


class SwaggerCategoryPatchSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField()
    color = serializers.IntegerField(min_value=0, max_value=8)
    title = serializers.CharField(max_length=100, required=False)
    rank = SwaggerRankSerializer(required=False)

    class Meta:
        model = Category
        fields = "__all__"


class SwaggerTodoPatchSerializer(serializers.ModelSerializer):
    todo_id = serializers.IntegerField()
    content = serializers.CharField(max_length=255, required=False)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False
    )
    date = serializers.DateField(allow_null=True, required=False)
    due_time = serializers.TimeField(allow_null=True, required=False)
    rank = SwaggerRankSerializer(required=False)
    is_completed = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = Todo
        fields = [
            "todo_id",
            "content",
            "category_id",
            "date",
            "due_time",
            "rank",
            "is_completed",
        ]


class SwaggerSubTodoPatchSerializer(serializers.ModelSerializer):
    subtodo_id = serializers.IntegerField()
    content = serializers.CharField(max_length=255, required=False)
    todo_id = serializers.PrimaryKeyRelatedField(
        queryset=Todo.objects.all(), required=False
    )
    date = serializers.DateField(allow_null=True, required=False)
    rank = SwaggerRankSerializer(required=False)
    is_completed = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = SubTodo
        fields = [
            "subtodo_id",
            "content",
            "todo_id",
            "date",
            "due_time",
            "rank",
            "is_completed",
        ]
