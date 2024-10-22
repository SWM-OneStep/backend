# todos/views.py


import asyncio
import json

import sentry_sdk
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from onestep_be.settings import openai_client
from todos.firebase_messaging import send_push_notification_device
from todos.models import Category, SubTodo, Todo, UserLastUsage
from todos.serializers import (
    CategorySerializer,
    GetTodoSerializer,
    SubTodoSerializer,
    TodoSerializer,
)
from todos.swagger_serializers import (
    SwaggerCategoryPatchSerializer,
    SwaggerCategorySerializer,
    SwaggerSubTodoPatchSerializer,
    SwaggerSubTodoSerializer,
    SwaggerTodoPatchSerializer,
    SwaggerTodoSerializer,
)
from todos.utils import sentry_validation_error, set_sentry_user

TODO_FCM_MESSAGE_TITLE = "Todo"
TODO_FCM_MESSAGE_BODY = "Todo가 변경되었습니다."
SUBTODO_FCM_MESSAGE_TITLE = "SubTodo"
SUBTODO_FCM_MESSAGE_BODY = "SubTodo가 변경되었습니다."
CATEGORY_FCM_MESSAGE_TITLE = "Category"
CATEGORY_FCM_MESSAGE_BODY = "Category가 변경되었습니다."

RATE_LIMIT_SECONDS = 10


class TodoView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Todo.objects.all()

    @swagger_auto_schema(
        tags=["Todo"],
        request_body=SwaggerTodoSerializer,
        operation_summary="Create a todo",
        responses={201: SwaggerTodoSerializer},
    )
    def post(self, request):
        """
        - 이 함수는 todo를 생성하는 함수입니다.
        - 입력 : date, due_time, content, category, parent_id
        - content 는 암호화 되어야 합니다.
        - category_id 는 category에 존재해야합니다.
        - content는 1자 이상 50자 이하여야합니다.

        구현해야할 내용
        - order 순서 정리
        - 암호화
        """

        try:
            data = request.data.copy()
            data["user_id"] = request.user.id

            set_sentry_user(request.user)
            serializer = TodoSerializer(
                context={"request": request}, data=data
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                send_push_notification_device(
                    request.auth.get("device"),
                    request.user,
                    TODO_FCM_MESSAGE_TITLE,
                    TODO_FCM_MESSAGE_BODY,
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            else:
                sentry_validation_error(
                    "TodoCreate", serializer.errors, request.user.id
                )
                return Response(
                    {"error": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        tags=["Todo"],
        manual_parameters=[
            openapi.Parameter(
                "start_date",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                description="start_date",
                required=False,
            ),
            openapi.Parameter(
                "end_date",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                description="end_date",
                required=False,
            ),
        ],
        operation_summary="Get a todo",
        responses={200: GetTodoSerializer},
    )
    def get(self, request):
        """
        - 이 함수는 daily todo list를 불러오는 함수입니다.
        - 입력 :  start_date, end_date
        - start_date와 end_date가 없는 경우 user_id에 해당하는 모든 todo를 불러옵니다.
        - start_date와 end_date가 있는 경우 user_id에 해당하는 todo 중 start_date와 end_date 사이에 있는 todo를 불러옵니다.
        - order 의 순서로 정렬합니다.
        """  # noqa: E501
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        user_id = request.user.id
        set_sentry_user(request.user)
        if user_id is None:
            sentry_sdk.capture_message("User_id not provided", level="error")
            return Response(
                {"error": "user_id must be provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            if (
                start_date is not None and end_date is not None
            ):  # start_date and end_date are not None
                todos = Todo.objects.get_daily_with_date(
                    user_id=user_id, start_date=start_date, end_date=end_date
                )
            else:
                todos = Todo.objects.get_with_user_id(
                    user_id=user_id
                ).order_by("rank")
        except Todo.DoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = GetTodoSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Todo"],
        request_body=SwaggerTodoPatchSerializer,
        operation_summary="Update a todo",
        responses={200: SwaggerTodoSerializer},
    )
    def patch(self, request):
        """
        - 이 함수는 todo를 수정하는 함수입니다.
        - 입력 : todo_id, 수정 내용
        - 수정 내용은 content, category, date, due_time 중 하나 이상이어야 합니다.
        - rank 의 경우 아래와 같이 제시된다.
            "rank" : {
                "prev_id" : 1,
                "next_id" : 3,
            }
        """  # noqa: E501
        set_sentry_user(request.user)
        todo_id = request.data.get("todo_id")
        if todo_id is None:
            sentry_sdk.capture_message("Todo_id not provided", level="error")
            return Response(
                {"error": "todo_id must be provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            todo = Todo.objects.get(id=todo_id, deleted_at__isnull=True)
        except Todo.DoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = TodoSerializer(
            context={"request": request},
            instance=todo,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            send_push_notification_device(
                request.auth.get("device"),
                request.user,
                TODO_FCM_MESSAGE_TITLE,
                TODO_FCM_MESSAGE_BODY,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            sentry_validation_error(
                "TodoPatch", serializer.errors, request.user.id
            )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        tags=["Todo"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "todo_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="todo_id"
                ),
            },
        ),
        operation_summary="Delete a todo",
        responses={200: SwaggerTodoSerializer},
    )
    def delete(self, request):
        """
        - 이 함수는 todo를 삭제하는 함수입니다.
        - 입력 : todo_id
        - todo_id에 해당하는 todo의 deleted_at 필드를 현재 시간으로 업데이트합니다.
        - deleted_at 필드가 null이 아닌 경우 이미 삭제된 todo입니다.
        - 해당 todo 에 속한 subtodo 도 전부 delete 를 해야함
        """  # noqa: E501
        set_sentry_user(request.user)
        todo_id = request.data.get("todo_id")
        if todo_id is None:
            sentry_sdk.capture_message("Todo_id not provided", level="error")
            return Response(
                {"error": "todo_id must be provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            todo = Todo.objects.get_with_id(id=todo_id)
            subtodos = SubTodo.objects.get_subtodos(todo.id)
            SubTodo.objects.delete_many(subtodos)
            Todo.objects.delete_instance(todo)
            send_push_notification_device(
                request.auth.get("device"),
                request.user,
                TODO_FCM_MESSAGE_TITLE,
                TODO_FCM_MESSAGE_BODY,
            )
            return Response(
                {"todo_id": todo.id, "message": "Todo deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Todo.DoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "Todo not found"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class SubTodoView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["SubTodo"],
        request_body=SwaggerSubTodoSerializer(many=True),
        operation_summary="Create a subtodo",
        responses={201: SwaggerSubTodoSerializer},
    )
    def post(self, request):
        """
        - 이 함수는 sub todo를 생성하는 함수입니다.
        - 입력 : todo, date, content
        - subtodo 는 리스트에 여러 객체가 들어간 형태를 가집니다.
        - content 는 암호화 되어야 합니다(// 미정)
        """
        set_sentry_user(request.user)
        data = request.data
        serializer = SubTodoSerializer(
            context={"request": request}, data=data, many=True
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            send_push_notification_device(
                request.auth.get("device"),
                request.user,
                SUBTODO_FCM_MESSAGE_TITLE,
                SUBTODO_FCM_MESSAGE_BODY,
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            sentry_validation_error(
                "SubTodoCreate", serializer.errors, request.user.id
            )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        tags=["SubTodo"],
        manual_parameters=[
            openapi.Parameter(
                "todo_id",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="todo_id",
                required=True,
            )
        ],
        operation_summary="Get a subtodo",
        responses={200: SwaggerSubTodoSerializer},
    )
    def get(self, request):
        """
        - 이 함수는 sub todo list를 불러오는 함수입니다.
        - 입력 : todo_id
        - parent_id에 해당하는 sub todo list를 불러옵니다.
        """
        set_sentry_user(request.user)
        todo_id = request.GET.get("todo_id")
        if todo_id is None:
            sentry_sdk.capture_message("Todo_id not provided", level="error")
            return Response(
                {"error": "todo_id must be provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            sub_todos = SubTodo.objects.get_subtodos(todo_id=todo_id)
            serializer = SubTodoSerializer(sub_todos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SubTodo.DoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "SubTodo not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        tags=["SubTodo"],
        request_body=SwaggerSubTodoPatchSerializer,
        operation_summary="Update a subtodo",
        responses={200: SwaggerSubTodoSerializer},
    )
    def patch(self, request):
        """
        - 이 함수는 sub todo를 수정하는 함수입니다.
        - 입력 : subtodo_id, 수정 내용
        - 수정 내용은 content, date, parent_id, rank 중 하나 이상이어야 합니다.
        - rank 의 경우 아래와 같이 수신됨
            "rank" : {
                "prev_id" : 1,
                "next_id" : 3,
            }
        """
        set_sentry_user(request.user)
        subtodo_id = request.data.get("subtodo_id")
        if subtodo_id is None:
            sentry_sdk.capture_message(
                "SubTodo_id not provided", level="error"
            )
            return Response(
                {"error": "subtodo_id must be provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            sub_todo = SubTodo.objects.get(
                id=subtodo_id, deleted_at__isnull=True
            )
        except SubTodo.DoesNotExist:
            return Response(
                {"error": "SubTodo not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = SubTodoSerializer(
            context={"request": request},
            instance=sub_todo,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            send_push_notification_device(
                request.auth.get("device"),
                request.user,
                SUBTODO_FCM_MESSAGE_TITLE,
                SUBTODO_FCM_MESSAGE_BODY,
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            sentry_validation_error(
                "SubTodoPatch", serializer.errors, request.user.id
            )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        tags=["SubTodo"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "subtodo_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="subtodo_id"
                ),
            },
        ),
        operation_summary="Delete a subtodo",
        responses={200: SwaggerSubTodoSerializer},
    )
    def delete(self, request):
        """
        - 이 함수는 sub todo를 삭제하는 함수입니다.
        - 입력 : subtodo_id
        - subtodo_id에 해당하는 sub todo의 deleted_at 필드를 현재 시간으로 업데이트합니다.
        - deleted_at 필드가 null이 아닌 경우 이미 삭제된 sub todo입니다.
        """  # noqa: E501
        set_sentry_user(request.user)
        subtodo_id = request.data.get("subtodo_id")
        if subtodo_id is None:
            sentry_sdk.capture_message(
                "SubTodo_id not provided", level="error"
            )
            return Response(
                {"error": "subtodo_id must be provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            sub_todo = SubTodo.objects.get_with_id(id=subtodo_id)
            SubTodo.objects.delete_instance(sub_todo)

            send_push_notification_device(
                request.auth.get("device"),
                request.user,
                SUBTODO_FCM_MESSAGE_TITLE,
                SUBTODO_FCM_MESSAGE_BODY,
            )
            return Response(
                {
                    "subtodo_id": sub_todo.id,
                    "message": "SubTodo deleted successfully",
                },
                status=status.HTTP_200_OK,
            )
        except SubTodo.DoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "SubTodo not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class CategoryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Category"],
        request_body=SwaggerCategorySerializer,
        operation_summary="Create a category",
        responses={201: SwaggerCategorySerializer},
    )
    def post(self, request):
        """
        - 이 함수는 category를 생성하는 함수입니다.
        - 입력 : title, color
        - title은 1자 이상 50자 이하여야합니다.
        - color는 7자여야합니다.
        """
        set_sentry_user(request.user)
        try:
            data = request.data.copy()
            data["user_id"] = request.user.id

            serializer = CategorySerializer(
                context={"request": request}, data=data
            )

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                send_push_notification_device(
                    request.auth.get("device"),
                    request.user,
                    CATEGORY_FCM_MESSAGE_TITLE,
                    CATEGORY_FCM_MESSAGE_BODY,
                )

                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            else:
                sentry_validation_error(
                    "CategoryCreate", serializer.errors, request.user.id
                )
                return Response(
                    {"error": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        tags=["Category"],
        request_body=SwaggerCategoryPatchSerializer,
        operation_summary="Update a category",
        responses={200: SwaggerCategorySerializer},
    )
    def patch(self, request):
        """
        - 이 함수는 category를 수정하는 함수입니다.
        - 입력 : category_id, 수정 내용
        - 수정 내용은 title, color 중 하나 이상이어야 합니다.
        - rank 의 경우 아래와 같이 수신됨
            "rank" : {
                "prev_id" : 1,
                "next_id" : 3,
            }
        """
        set_sentry_user(request.user)
        category_id = request.data.get("category_id")
        if category_id is None:
            sentry_sdk.capture_message(
                "Category_id not provided", level="error"
            )
            return Response(
                {"error": "category_id must be provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if "user_id" in request.data:
            return Response(
                {"error": "user_id cannot be updated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            category = Category.objects.get(
                id=category_id, deleted_at__isnull=True
            )
        except Category.DoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = CategorySerializer(
            context={"request": request},
            instance=category,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            send_push_notification_device(
                request.auth.get("device"),
                request.user,
                CATEGORY_FCM_MESSAGE_TITLE,
                CATEGORY_FCM_MESSAGE_BODY,
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            sentry_validation_error(
                "CategoryPatch", serializer.errors, request.user.id
            )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        tags=["Category"],
        operation_summary="Get a category",
        responses={200: SwaggerCategorySerializer},
    )
    def get(self, request):
        """
        - 이 함수는 category list를 불러오는 함수입니다.
        - 입력 : 없음
        - user_id에 해당하는 category list를 불러옵니다.
        """
        set_sentry_user(request.user)
        try:
            user_id = request.user.id
            if user_id is None:
                sentry_sdk.capture_message(
                    "User_id not provided", level="error"
                )
                return Response(
                    {"error": "user_id must be provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            categories = Category.objects.get_with_user_id(user_id=user_id)
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        tags=["Category"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "category_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Category_id"
                ),
            },
        ),
        operation_summary="Delete a category",
        responses={200: SwaggerCategorySerializer},
    )
    def delete(self, request):
        """
        - 이 함수는 category를 삭제하는 함수입니다.
        - 입력 : category_id
        - category_id에 해당하는 category의 deleted_at 필드를 현재 시간으로 업데이트합니다.
        - deleted_at 필드가 null이 아닌 경우 이미 삭제된 category입니다.
        """  # noqa: E501
        try:
            set_sentry_user(request.user)
            category_id = request.data.get("category_id")
            if category_id is None:
                sentry_sdk.capture_message(
                    "Category_id not provided", level="error"
                )
                return Response(
                    {"error": "category_id must be provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            category = Category.objects.get_with_id(id=category_id)
            Category.objects.delete_instance(category)
            send_push_notification_device(
                request.auth.get("device"),
                request.user,
                CATEGORY_FCM_MESSAGE_TITLE,
                CATEGORY_FCM_MESSAGE_BODY,
            )
            return Response(
                {
                    "category_id": category.id,
                    "message": "Category deleted successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Category.DoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class InboxView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["InboxTodo"],
        manual_parameters=[
            openapi.Parameter(
                "user_id",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="user_id",
                required=True,
            ),
        ],
        operation_summary="Get Inbox todo",
        responses={200: GetTodoSerializer},
    )
    def get(self, request):
        """
        - 이 함수는 daily todo list를 불러오는 함수입니다.
        - 입력 :  없음
        - order 의 순서로 정렬합니다.
        """
        try:
            set_sentry_user(request.user)
            user_id = request.user.id
            if user_id is None:
                sentry_sdk.capture_message(
                    "User_id not provided", level="error"
                )
                return Response(
                    {"error": "user_id must be provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            todos = Todo.objects.get_inbox(user_id=user_id)
            serializer = GetTodoSerializer(todos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Todo.DoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "Inbox is Empty"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class RecommendSubTodo(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["RecommendSubTodo"],
        manual_parameters=[
            openapi.Parameter(
                "todo_id",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="todo_id",
                required=True,
            ),
        ],
        operation_summary="Recommend subtodo",
        responses={200: SubTodoSerializer},
    )
    def get(self, request):
        """
        - 이 함수는 sub todo를 추천하는 함수입니다.
        """
        set_sentry_user(request.user)

        user_id = request.user.id
        try:
            flag, message = UserLastUsage.check_rate_limit(
                user_id=user_id, RATE_LIMIT_SECONDS=RATE_LIMIT_SECONDS
            )

            if flag is False:
                return Response(
                    {"error": message},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            todo_id = request.GET.get("todo_id")
            if todo_id is None:
                sentry_sdk.capture_message(
                    "Todo_id not provided", level="error"
                )
                return Response(
                    {"error": "todo_id must be provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # 비동기적으로 OpenAI API 호출 처리
            todo = Todo.objects.get_with_id(id=todo_id)
            todo_data = {
                "id": todo.id,
                "content": todo.content,
                "date": todo.date,
                "due_time": todo.due_time,
                "category_id": todo.category_id,
                "rank": todo.rank,
                "is_completed": todo.is_completed,
            }
            completion = asyncio.run(self.get_openai_completion(todo_data))
            return Response(
                json.loads(completion.choices[0].message.content),
                status=status.HTTP_200_OK,
            )
        except Todo.DoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    # 비동기적으로 OpenAI API를 호출하는 함수
    async def get_openai_completion(self, todo):
        return await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """너는 퍼스널 매니저야.
        너가 하는 일은 이 사람이 할 이야기를 듣고 약 1시간 정도면 끝낼 수 있도록 작업을 나눠주는 식으로 진행할 거야.
        아래는 너가 나눠줄 작업 형식이야.
        { id : 1, content: "3학년 2학기 운영체제 중간고사 준비", date="2024-09-01", due_time="2024-09-24"}
        이런  형식으로 작성된 작업을 받았을 때 너는 이 작업을 어떻게 나눠줄 것인지를 알려주면 돼.
        Output a JSON object structured like:
        {id, content, date, due_time, category_id, rank, is_completed, children : [
        {content, date, todo(parent todo id)}, ... ,{content, date, todo(parent todo id)}]}
        [조건]
        - date 는 부모의 date를 따를 것
        - 작업은 한 서브투두를 해결하는데 1시간 정도로 이루어지도록 제시할 것
        - 언어는 주어진 todo content의 언어에 따를 것
        """,  # noqa: E501
                },
                {
                    "role": "user",
                    "content": f"id: {todo["id"]}, \
                content: {todo["content"]}, \
                date: {todo["date"]}, \
                due_time: {todo["due_time"]}, \
                category_id: {todo["category_id"]}, \
                rank: {todo["rank"]}, \
                is_completed: {todo["is_completed"]}",
                },
            ],
            response_format={"type": "json_object"},
        )
