# todos/serializers.py
from rest_framework import serializers
from .models import Todo, Category, SubTodo
from accounts.models import User
import django.utils.timezone as timezone

from todos.utils import validate_lexo_order
import re

class CategorySerializer(serializers.ModelSerializer):

    def validate_user_id(self, data):
        try:
            User.objects.get(id=data.id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        return data
    
    def validate_color(self, data):
        hex_color_pattern = r'^#([A-Fa-f0-9]{6})$'
        match = re.match(hex_color_pattern, data)
        if bool(match) is False:
            raise serializers.ValidationError("Color code is invalid")
        return data
    
    def validate(self, data):
        request = self.context['request']
        if request.method == 'PATCH':
            if not any(data.get(field) for field in ['color', 'title', 'order']):
                raise serializers.ValidationError("At least one of color, title, order must be provided")
            return data
        elif request.method == 'POST':
            user_id = data.get('user_id')
            last_category = Category.objects.filter(user_id=user_id, deleted_at__isnull=True).order_by('-order').first()
            if last_category is not None:
                last_order = last_category.order
                if validate_lexo_order(prev=last_order, next=None, updated=data['order']) is False:  
                        raise serializers.ValidationError("Order is invalid")
        return data
    
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
    children = SubTodoSerializer(many=True, read_only=True, source='todos') 
    class Meta:
        model = Todo
        fields = ['id', 'content', 'category_id', 'start_date', 'end_date', 'user_id', 'order', 'is_completed', 'children']



class TodoSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=255)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    start_date = serializers.DateField(allow_null=True, required=False)
    end_date = serializers.DateField(allow_null=True, required=False)
    order = serializers.CharField(max_length=255)
    is_completed = serializers.BooleanField(default=False, required=False)
        
    def validate_category_id(self, data):
        try:
            Category.objects.get(id=data.id)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category does not exist")
        return data
        
    def validate_user_id(self, data):
        try:
            User.objects.get(id=data.id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        return data

    def validate(self, data):
        request = self.context['request']
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)

        if start_date is not None and end_date is not None:
            if start_date > end_date:
                raise serializers.ValidationError("start date should be less than end date")
        if request.method == 'PATCH':
            if not any(data.get(field) for field in ['content', 'category_id', 'start_date', 'end_date', 'is_completed', 'order']):
                raise serializers.ValidationError("At least one of content, category_id, start_date, end_date, is_completed must be provided")
            return data
        
        elif request.method == 'POST':
            user_id = data.get('user_id')
            last_todo = Todo.objects.filter(user_id=user_id, deleted_at__isnull=True).order_by('-order').first()
            if last_todo is not None:
                last_order = last_todo.order
                if validate_lexo_order(prev=last_order, next=None, updated=data['order']) is False:  
                        raise serializers.ValidationError("Order is invalid")
        return data
        
    class Meta:
        model = Todo
        fields = ['id', 'content', 'category_id', 'start_date', 'end_date', 'user_id', 'order', 'is_completed']

    def update(self, instance, validated_data):
        # Update the fields as usual
        for attr, value in validated_data.items():
            if attr == 'order':
                instance.order = value
                continue
            setattr(instance, attr, value)
        
        # Set the updated_at field to the current time
        instance.updated_at = timezone.now()
        instance.save()
        return instance


