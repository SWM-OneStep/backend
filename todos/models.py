from django.db import models

# Create your models here.
class Todo(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=255)
    category = models.CharField(max_length=7)
    start_date = models.DateField()
    deadline = models.DateField()
    parent_id = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    user_id = models.ForeignKey('accounts.User', on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now  =True)
    deleted_at = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.content
    
