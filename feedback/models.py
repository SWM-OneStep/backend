from django.db import models

from accounts.models import User


# Create your models here.
class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ("bug", "버그"),
        ("feature", "기능 요청"),
        ("feedback", "일반 피드백"),
    ]
    STATUS_CHOICES = [
        ("pending", "대기 중"),
        ("processing", "처리 중"),
        ("completed", "완료"),
    ]

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
