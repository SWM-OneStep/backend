# todos/serializers.py
from rest_framework import serializers
from .models import Todo, Category
from django.http import QueryDict
from accounts.models import User
import django.utils.timezone as timezone


class TodoSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=50)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    start_date = serializers.DateField(allow_null=True, required=False)
    deadline = serializers.DateField(allow_null=True, required=False)
    due_date = serializers.DateField(allow_null=True, required=False)
    parent_id = serializers.PrimaryKeyRelatedField(queryset=Todo.objects.all(), allow_null=True, required=False)
    order = serializers.CharField(max_length = 255)
    is_completed = serializers.BooleanField(default=False)

    
    class Meta:
        model = Todo
        fields = ['id', 'content', 'category_id', 'start_date', 'deadline', 'due_date', 'parent_id', 'user_id', 'order', 'is_completed', 'depth']
    def validate(self, data):
        parent = data.get('parent_id', None)
        depth = 1
        if parent is None:
            depth = 1
        elif parent.parent_id is None:
            depth = 2
        elif parent.parent_id.parent_id is None:
            depth = 3
        else:
            depth = 4
        
        if depth > 3:
            raise serializers.ValidationError("depth should be less than 4")
        
        return data

    
    def to_internal_value(self, data):
        return super().to_internal_value(data)

class TodoUpdateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=50)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)
    start_date = serializers.DateField(allow_null=True, required=False)
    deadline = serializers.DateField(allow_null=True, required=False)
    due_date = serializers.DateField(allow_null=True, required=False)
    parent_id = serializers.PrimaryKeyRelatedField(queryset=Todo.objects.all(), allow_null=True, required=False)
    order = serializers.CharField(max_length = 255, required=False)
    is_completed = serializers.BooleanField(default=False, required=False)
    
    def validate(self, data):
        parent = data.get('parent_id', None)
        depth = 1
        if parent is None:
            depth = 1
        elif parent.parent_id is None:
            depth = 2
        elif parent.parent_id.parent_id is None:
            depth = 3
        else:
            depth = 4
        
        if depth > 3:
            raise serializers.ValidationError("depth should be less than 4")
        return data
        
    class Meta:
        model = Todo
        fields = ['id', 'content', 'category_id', 'start_date', 'deadline', 'due_date', 'parent_id', 'user_id', 'order', 'is_completed', 'depth']

    def update(self, instance, validated_data):
        # Update the fields as usual
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Set the updated_at field to the current time
        instance.updated_at = timezone.now()
        instance.save()
        return instance