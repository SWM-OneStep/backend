# todos/serializers.py
from rest_framework import serializers
from .models import Todo
from django.http import QueryDict
from accounts.models import User


class TodoSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=50)
    category = serializers.CharField(max_length=7)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    start_date = serializers.DateField()
    deadline = serializers.DateField()
    due_date = serializers.DateField(allow_null=True, required=False)
    parent_id = serializers.PrimaryKeyRelatedField(queryset=Todo.objects.all(), allow_null=True, required=False)
    order = serializers.IntegerField(default=0)
    is_completed = serializers.BooleanField(default=False)
    
    class Meta:
        model = Todo
        fields = ['id', 'content', 'category', 'start_date', 'deadline', 'due_date', 'parent_id', 'user_id', 'order', 'is_completed']
    def to_internal_value(self, data):
        return super().to_internal_value(data)