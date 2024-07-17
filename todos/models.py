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
    deadline = models.DateField(null = True)
    due_date = models.DateField(null = True)
    parent_id = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    
    @property
    def depth(self):
        if self.parent_id is None:
            return 1
        elif self.parent_id.parent_id is None:
            return 2
        else:
            return 3
        
    def __str__(self):
        return self.content
    
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    title_color = models.CharField(max_length=7)
    subtitle_color = models.CharField(max_length=7)
    content_color = models.CharField(max_length=7)
