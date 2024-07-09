# todos/serializers.py
from rest_framework import serializers
from .models import Todo
from accounts.models import User

class TodoSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=255)
    category = serializers.CharField(max_length=7)
    start_date = serializers.DateField()
    deadline = serializers.DateField()
    parent_id = serializers.PrimaryKeyRelatedField(queryset=Todo.objects.all(), allow_null=True, required=False)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    class Meta:
        model = Todo
        fields = ['id', 'content', 'category', 'start_date', 'deadline', 'parent_id', 'user_id']
