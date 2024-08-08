# todos/serializers.py
from rest_framework import serializers
from .models import Todo, Category, SubTodo

class SwaggerOrderserializer(serializers.ModelSerializer):
    prev_id = serializers.IntegerField()
    next_id = serializers.IntegerField()
    updated_order = serializers.CharField(max_length=255)

    class Meta:
        model = Todo
        fields = ['prev_id', 'next_id', 'updated_order']

class SwaggerCategoryPatchSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField()
    color = serializers.CharField(max_length=7, required=False)
    title = serializers.CharField(max_length=100, required=False)
    order = SwaggerOrderserializer(required=False)

    class Meta:
        model = Category
        fields = "__all__"

class SwaggerTodoPatchSerializer(serializers.ModelSerializer):
    todo_id = serializers.IntegerField()
    content = serializers.CharField(max_length=255, required=False)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)
    start_date = serializers.DateField(allow_null=True, required=False)
    end_date = serializers.DateField(allow_null=True, required=False)
    order = SwaggerOrderserializer(required=False)
    is_completed = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = Todo
        fields = ['todo_id', 'content', 'category_id', 'start_date', 'end_date', 'order', 'is_completed']

class SwaggerSubTodoPatchSerializer(serializers.ModelSerializer):
    subtodo_id = serializers.IntegerField()
    content = serializers.CharField(max_length=255, required=False)
    todo = serializers.PrimaryKeyRelatedField(queryset=Todo.objects.all(), required=False)
    date = serializers.DateField(allow_null=True, required=False)
    order = SwaggerOrderserializer(required=False)
    is_completed = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = SubTodo
        fields = ['subtodo_id', 'content', 'todo', 'date', 'order', 'is_completed']
