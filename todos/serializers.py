# todos/serializers.py
from rest_framework import serializers
from .models import Todo, Category, SubTodo
from accounts.models import User
import django.utils.timezone as timezone

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"

class SubTodoSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=255)
    todo = serializers.PrimaryKeyRelatedField(queryset=Todo.objects.all(), required=True)
    date = serializers.DateField(required=False, allow_null=True)
    order = serializers.CharField(max_length=255)
    is_completed = serializers.BooleanField(default=False)

    class Meta:
        model = SubTodo
        fields = "__all__"

class GetTodoSerializer(serializers.ModelSerializer):
    children = SubTodoSerializer(many=True, read_only=True, source='subtodos') 
    class Meta:
        model = Todo
        fields = ['id', 'content', 'category_id', 'start_date', 'end_date', 'user_id', 'order', 'is_completed', 'children']



class TodoSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=255)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    start_date = serializers.DateField(allow_null=True, required=False)
    end_date = serializers.DateField(allow_null=True, required=False)
    order = serializers.CharField(max_length = 255, required=False)
    is_completed = serializers.BooleanField(default=False, required=False)
    
    def validate(self, data):
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)

        if start_date is not None and end_date is not None:
            if start_date > end_date:
                raise serializers.ValidationError("start date should be less than end date")

        return data
        
    class Meta:
        model = Todo
        fields = ['id', 'content', 'category_id', 'start_date', 'end_date', 'user_id', 'order', 'is_completed']

    def update(self, instance, validated_data):
        # Update the fields as usual
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Set the updated_at field to the current time
        instance.updated_at = timezone.now()
        instance.save()
        return instance


