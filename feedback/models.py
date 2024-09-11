from django.db import models

from accounts.models import User


# Create your models here.
class Feedback(models.Model):
    class CategoryProvider(models.TextChoices):
        Bug = "bug", "버그"
        Feature = "feature", "기능 요청"
        Feedback = "feedback", "일반 피드백"

    class StatusProvider(models.TextChoices):
        Pending = "pending", "대기 중"
        Processing = "processing", "처리 중"
        Completed = "completed", "완료"

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=20, choices=CategoryProvider.choices
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=StatusProvider.choices,
        default=StatusProvider.Pending,
    )
