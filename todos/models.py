from django.db import models



class TimeStamp(models.Model):
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

        
class Todo(TimeStamp):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=255)
    category = models.CharField(max_length=7)
    start_date = models.DateField(null = True)
    deadline = models.DateField(null = True)
    due_date = models.DateField(null = True)
    parent_id = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    user_id = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.content
    