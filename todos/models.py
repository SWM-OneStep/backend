from django.db import models
from django.db.models import Count, Prefetch, Q
from django.utils import timezone

from accounts.models import User


class TodosManager(models.Manager):
    def delete_instance(self, instance):
        instance.deleted_at = timezone.now()
        instance.save()
        return instance

    def delete_many(self, instances):
        for instance in instances:
            instance.deleted_at = timezone.now()
            instance.save()
        return instances

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def get_with_id(self, id):
        return self.get_queryset().filter(id=id).first()

    def get_with_user_id(self, user_id):
        return self.get_queryset().filter(user_id=user_id).order_by("order")

    def get_subtodos(self, todo_id):
        return self.get_queryset().filter(todo=todo_id).order_by("order")

    def get_inbox(self, user_id):
        return (
            Todo.objects.filter(user_id=user_id, deleted_at__isnull=True)
            .annotate(
                subtodos_count=Count(
                    "subtodos",
                    filter=Q(
                        subtodos__deleted_at__isnull=True,
                        subtodos__date__isnull=True,
                    ),
                )
            )
            .filter(
                Q(end_date__isnull=True, start_date__isnull=True)
                | Q(subtodos_count__gt=0)
            )
            .prefetch_related(
                Prefetch(
                    "subtodos",
                    queryset=SubTodo.objects.filter(
                        deleted_at__isnull=True, date__isnull=True
                    ).order_by("order"),
                )
            )
            .order_by("order")
        )

    def get_daily_with_date(self, user_id, start_date, end_date):
        return (
            Todo.objects.filter(user_id=user_id, deleted_at__isnull=True)
            .filter(
                (
                    Q(start_date__isnull=True)
                    | Q(start_date__lte=end_date, start_date__gte=start_date)
                )
                | (
                    Q(end_date__isnull=True)
                    | Q(end_date__lte=end_date, end_date__gte=start_date)
                )
                | (Q(start_date__lte=start_date, end_date__gte=end_date))
            )
            .exclude(start_date__isnull=True, end_date__isnull=True)
            .order_by("order")
            .prefetch_related(
                Prefetch(
                    "subtodos",
                    queryset=SubTodo.objects.filter(
                        deleted_at__isnull=True, date__isnull=False
                    ).order_by("order"),
                )
            )
        )

    def get_daily(self, user_id):
        return (
            Todo.objects.filter(user_id=user_id, deleted_at__isnull=True)
            .filter(Q(end_date__isnull=False) | Q(start_date__isnull=False))
            .order_by("order")
            .prefetch_related(
                Prefetch(
                    "subtodos",
                    queryset=SubTodo.objects.filter(
                        deleted_at__isnull=True, date__isnull=False
                    ).order_by("order"),
                )
            )
        )


class TimeStamp(models.Model):
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class Todo(TimeStamp):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=255)
    category_id = models.ForeignKey("Category", on_delete=models.CASCADE)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)

    objects = TodosManager()

    def __str__(self):
        return self.content


class SubTodo(TimeStamp):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=255)
    todo = models.ForeignKey(
        "Todo", on_delete=models.CASCADE, related_name="subtodos"
    )
    date = models.DateField(null=True)
    order = models.CharField(max_length=255, null=True)
    is_completed = models.BooleanField(default=False)

    objects = TodosManager()

    def __str__(self):
        return self.content


class Category(TimeStamp):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    color = models.CharField(max_length=7)
    title = models.CharField(max_length=100, null=True)
    order = models.CharField(max_length=255, null=True)

    objects = TodosManager()


# Prompt Models
class BasePrompt(models.Model):
    todo_id = models.ForeignKey(Todo, on_delete=models.PROTECT)
    user_id = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class GeneratedSubTodo(BasePrompt):
    id = models.AutoField(primary_key=True)
    content = models.TextField(max_length=255)
    is_selected = models.BooleanField(default=False)


class PromptQuestion(BasePrompt):
    id = models.AutoField(primary_key=True)
    question = models.TextField(max_length=255)
    answer = models.TextField(max_length=255, null=True)


class PromptInjection(BasePrompt):
    id = models.AutoField(primary_key=True)
    injection_reason = models.TextField(max_length=255)
