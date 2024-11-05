from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count, Prefetch, Q
from django.utils import timezone

from accounts.models import User
from Lexorank.src.lexo_rank import LexoRank


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

    def get_next_rank_subtodo(self, user_id):
        get_list = (
            SubTodo.objects.filter(todo_id__user_id=user_id)
            .select_related("todo_id")
            .last()
        )
        if get_list is None:
            return str(LexoRank.middle())
        return str((LexoRank.parse(get_list.rank)).gen_next())

    def get_next_rank(self, user_id):
        get_list = (
            self.get_queryset().filter(user_id=user_id).order_by("rank").last()
        )
        if get_list is None:
            return str(LexoRank.middle())
        return str(LexoRank.gen_next(LexoRank.parse(get_list.rank)))

    def get_update_rank(self, instance, prev_id, next_id):
        if prev_id is None and next_id is None:
            return instance.rank
        elif prev_id is None:  # Move to the top
            get_next_rank = self.get_queryset().get(id=next_id).rank
            get_rank = str(LexoRank.parse(get_next_rank).gen_prev())
            return get_rank
        elif next_id is None:  # Move to the bottom
            get_prev_rank = self.get_queryset().get(id=prev_id).rank
            get_rank = str(LexoRank.parse(get_prev_rank).gen_next())
            return get_rank
        else:  # Move to after prev_id
            prev_rank = self.get_queryset().get(id=prev_id).rank
            prev_lexo = LexoRank.parse(prev_rank)
            next_rank = self.get_queryset().get(id=next_id).rank
            next_instance = LexoRank.parse(next_rank)
            return str(prev_lexo.between(next_instance))

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def get_with_id(self, id):
        instance = self.get_queryset().filter(id=id).first()
        if instance is None:
            raise ObjectDoesNotExist(f"No object found with id {id}")
        return instance

    def get_with_user_id(self, user_id):
        instance = self.get_queryset().filter(user_id=user_id).order_by("rank")
        if instance is None:
            raise ObjectDoesNotExist(f"No object found with user_id {user_id}")
        return instance

    def get_subtodos(self, todo_id):
        instance = self.get_queryset().filter(todo_id=todo_id).order_by("rank")
        if instance is None:
            raise ObjectDoesNotExist(f"No object found with todo_id {todo_id}")
        return instance

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
            .filter(Q(date__isnull=True) | Q(subtodos_count__gt=0))
            .prefetch_related(
                Prefetch(
                    "subtodos",
                    queryset=SubTodo.objects.filter(
                        deleted_at__isnull=True, date__isnull=True
                    ).order_by("rank"),
                )
            )
            .order_by("rank")
        )

    def get_daily_with_date(self, user_id, start_date, end_date):
        return (
            Todo.objects.filter(user_id=user_id, deleted_at__isnull=True)
            .filter(Q(date__gte=start_date, date__lte=end_date))
            .exclude(date__isnull=True)
            .order_by("rank")
            .prefetch_related(
                Prefetch(
                    "subtodos",
                    queryset=SubTodo.objects.filter(
                        deleted_at__isnull=True, date__isnull=False
                    ).order_by("rank"),
                )
            )
        )

    def get_daily(self, user_id):
        return (
            Todo.objects.filter(user_id=user_id, deleted_at__isnull=True)
            .filter(date__isnull=False)
            .order_by("order")
            .prefetch_related(
                Prefetch(
                    "subtodos",
                    queryset=SubTodo.objects.filter(
                        deleted_at__isnull=True, date__isnull=False
                    ).order_by("rank"),
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
    due_time = models.TimeField(null=True)
    date = models.DateField(null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

    rank = models.CharField(max_length=255, default="0|hzzzzz:")

    objects = TodosManager()

    def __str__(self):
        return self.content


class SubTodo(TimeStamp):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=255)
    todo_id = models.ForeignKey(
        "Todo", on_delete=models.CASCADE, related_name="subtodos"
    )
    due_time = models.TimeField(null=True, blank=True)
    date = models.DateField(null=True)
    is_completed = models.BooleanField(default=False)

    rank = models.CharField(max_length=255, default="0|hzzzzz:")

    objects = TodosManager()

    def __str__(self):
        return self.content


class Category(TimeStamp):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    color = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(8)]
    )
    title = models.CharField(max_length=100, null=True)

    rank = models.CharField(max_length=255, default="0|hzzzzz:")

    objects = TodosManager()


class UserLastUsage(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.PROTECT)
    last_used_at = models.DateTimeField(null=False)

    @classmethod
    def check_rate_limit(cls, user_id: int, RATE_LIMIT_SECONDS: int):
        try:
            user = User.objects.get(id=user_id)
            user_last_usage, created = cls.objects.get_or_create(
                user_id=user, defaults={"last_used_at": timezone.now()}
            )
            if user.is_premium:
                user_last_usage.last_used_at = timezone.now()
                user_last_usage.save(update_fields=["last_used_at"])
                return True, "Premium user"
            if not created:
                now = timezone.now()
                if (
                    user_last_usage.last_used_at
                    + timezone.timedelta(seconds=RATE_LIMIT_SECONDS)
                    > now
                ):
                    return False, "Rate limit exceeded"
                else:
                    user_last_usage.last_used_at = now
                    user_last_usage.save(update_fields=["last_used_at"])
                    return True, "Updated"
            else:
                return True, "Created"
        except User.DoesNotExist:
            return False, "User does not exist"
        except Exception as e:
            return False, f"An error occurred: {str(e)}"
