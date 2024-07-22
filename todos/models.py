from django.db import models
from accounts.models import User


class TimeStamp(models.Model):
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

        
class Todo(TimeStamp):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=255)
    category_id = models.ForeignKey('Category', on_delete=models.CASCADE, default=1)
    start_date = models.DateField(null = True)
    end_date = models.DateField(null = True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
        
    def __str__(self):
        return self.content
    

class SubTodo(TimeStamp):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=255)
    todo_id = models.ForeignKey('Todo', on_delete=models.CASCADE, related_name='subtodos')
    date = models.DateField()
    order = models.CharField(max_length=255, null=True)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.content


class Category(TimeStamp):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    color = models.CharField(max_length=7)
    title = models.CharField(max_length=100, null=True)
    order = models.CharField(max_length=255, null=True)
