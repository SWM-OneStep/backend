from rest_framework import serializers

from accounts.models import User
from feedback.models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=True
    )
    title = serializers.CharField(max_length=200, required=True)
    category = serializers.ChoiceField(
        choices=Feedback.CategoryProvider.choices, required=True
    )
    description = serializers.CharField(required=True)

    class Meta:
        model = Feedback
        fields = "__all__"
