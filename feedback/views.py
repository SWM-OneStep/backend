# Create your views here.# todos/views.py

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from feedback.serializers import (
    FeedbackSerializer,
)


class FeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Feedback"],
        request_body=FeedbackSerializer,
        operation_summary="Create a Feedback",
        responses={201: FeedbackSerializer},
    )
    def post(self, request):
        """
        - 이 함수는 Feedback을 생성하는 함수입니다.
        - 입력 : user_id, title, category, description
        """
        data = request.data
        # category_id validation
        serializer = FeedbackSerializer(
            context={"request": request}, data=data
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
