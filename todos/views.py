# todos/views.py
import json

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from onestep_be.settings import client
from todos.models import Category, SubTodo, Todo
from todos.serializers import (
    CategorySerializer,
    GeneratedSubTodoSerializer,
    GetTodoSerializer,
    PromptInjectionSerializer,
    PromptQuestionSerializer,
    SubTodoSerializer,
    TodoSerializer,
)
from todos.swagger_serializers import (
    SwaggerCategoryPatchSerializer,
    SwaggerSubTodoPatchSerializer,
    SwaggerTodoPatchSerializer,
)
from todos.utils import (
    create_user_prompt,
    get_planner_system_prompt,
)


class TodoView(APIView):
    permission_classes = [AllowAny]
    queryset = Todo.objects.all()

    @swagger_auto_schema(
        tags=["Todo"],
        request_body=TodoSerializer,
        operation_summary="Create a todo",
        responses={201: TodoSerializer},
    )
    def post(self, request):
        """
        - 이 함수는 todo를 생성하는 함수입니다.
        - 입력 : user_id, start_date, deadline, content, category, parent_id
        - content 는 암호화 되어야 합니다.
        - deadline 은 항상 start_date 와 같은 날이거나 그 이후여야합니다
        - category_id 는 category에 존재해야합니다.
        - content는 1자 이상 50자 이하여야합니다.
        - user_id 는 user 테이블에 존재해야합니다.
        - parent_id는 todo 테이블에 이미 존재해야합니다.
        - parent_id가 없는 경우 null로 처리합니다.
        - parent_id는 자기 자신을 참조할 수 없습니다.

        구현해야할 내용
        - order 순서 정리
        - 암호화
        """
        data = request.data
        # category_id validation
        serializer = TodoSerializer(context={"request": request}, data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        tags=["Todo"],
        manual_parameters=[
            openapi.Parameter(
                "user_id",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="user_id",
                required=True,
            ),
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
        - 입력 :  user_id(필수), start_date, end_date
        - start_date와 end_date가 없는 경우 user_id에 해당하는 모든 todo를 불러옵니다.
        - start_date와 end_date가 있는 경우 user_id에 해당하는 todo 중 start_date와 end_date 사이에 있는 todo를 불러옵니다.
        - order 의 순서로 정렬합니다.
        """  # noqa: E501
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        user_id = request.GET.get("user_id")
        if user_id is None:
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
            else:  # start_date and end_date are None
                todos = Todo.objects.get_with_user_id(
                    user_id=user_id
                ).order_by("order")
        except Todo.DoesNotExist:
            return Response(
                {"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = GetTodoSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Todo"],
        request_body=SwaggerTodoPatchSerializer,
        operation_summary="Update a todo",
        responses={200: TodoSerializer},
    )
    def patch(self, request):
        """
        - 이 함수는 todo를 수정하는 함수입니다.
        - 입력 : todo_id, 수정 내용
        - 수정 내용은 content, category, start_date, end_date 중 하나 이상이어야 합니다.
        - order 의 경우 아래와 같이 제시된다.
            "order" : {
                "prev_id" : 1,
                "next_id" : 3,
                "updated_order" : "0|asdf:"
            }
        """  # noqa: E501
        todo_id = request.data.get("todo_id")
        try:
            todo = Todo.objects.get(id=todo_id, deleted_at__isnull=True)
        except Todo.DoesNotExist:
            return Response(
                {"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if "order" in request.data:
            nested_order = request.data.get("order")
            request.data["order"] = nested_order.get("updated_order")
            request.data["patch_order"] = nested_order
        serializer = TodoSerializer(
            context={"request": request},
            instance=todo,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
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
        responses={200: TodoSerializer},
    )
    def delete(self, request):
        """
        - 이 함수는 todo를 삭제하는 함수입니다.
        - 입력 : todo_id
        - todo_id에 해당하는 todo의 deleted_at 필드를 현재 시간으로 업데이트합니다.
        - deleted_at 필드가 null이 아닌 경우 이미 삭제된 todo입니다.
        - 해당 todo 에 속한 subtodo 도 전부 delete 를 해야함
        """  # noqa: E501
        todo_id = request.data.get("todo_id")

        try:
            todo = Todo.objects.get_with_id(id=todo_id)
            subtodos = SubTodo.objects.get_subtodos(todo.id)
            SubTodo.objects.delete_many(subtodos)
            Todo.objects.delete_instance(todo)
        except Todo.DoesNotExist:
            return Response(
                {"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"todo_id": todo.id, "message": "Todo deleted successfully"},
            status=status.HTTP_200_OK,
        )


class SubTodoView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["SubTodo"],
        request_body=SubTodoSerializer(many=True),
        operation_summary="Create a subtodo",
        responses={201: SubTodoSerializer},
    )
    def post(self, request):
        """
        - 이 함수는 sub todo를 생성하는 함수입니다.
        - 입력 : todo, date, content, order
        - subtodo 는 리스트에 여러 객체가 들어간 형태를 가집니다.
        - content 는 암호화 되어야 합니다(// 미정)
        - date 는 parent의 start_date와 end_date의 사이여야 합니다.
        """
        data = request.data
        serializer = SubTodoSerializer(
            context={"request": request}, data=data, many=True
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
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
        responses={200: SubTodoSerializer},
    )
    def get(self, request):
        """
        - 이 함수는 sub todo list를 불러오는 함수입니다.
        - 입력 : todo_id
        - parent_id에 해당하는 sub todo list를 불러옵니다.
        """
        todo_id = request.GET.get("todo_id")
        try:
            sub_todos = SubTodo.objects.get_subtodos(todo_id=todo_id)
        except SubTodo.DoesNotExist:
            return Response(
                {"error": "SubTodo not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SubTodoSerializer(sub_todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["SubTodo"],
        request_body=SwaggerSubTodoPatchSerializer,
        operation_summary="Update a subtodo",
        responses={200: SubTodoSerializer},
    )
    def patch(self, request):
        """
        - 이 함수는 sub todo를 수정하는 함수입니다.
        - 입력 : subtodo_id, 수정 내용
        - 수정 내용은 content, date, parent_id 중 하나 이상이어야 합니다.
        - order 의 경우 아래와 같이 수신됨
            "order" : {
                "prev_id" : 1,
                "next_id" : 3,
                "updated_order" : "0|asdf:"
            }
        """
        subtodo_id = request.data.get("subtodo_id")
        try:
            sub_todo = SubTodo.objects.get(
                id=subtodo_id, deleted_at__isnull=True
            )
        except SubTodo.DoesNotExist:
            return Response(
                {"error": "SubTodo not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if "order" in request.data:
            nested_order = request.data.get("order")
            request.data["order"] = nested_order.get("updated_order")
            request.data["patch_order"] = nested_order
        serializer = SubTodoSerializer(
            context={"request": request},
            instance=sub_todo,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
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
        responses={200: SubTodoSerializer},
    )
    def delete(self, request):
        """
        - 이 함수는 sub todo를 삭제하는 함수입니다.
        - 입력 : subtodo_id
        - subtodo_id에 해당하는 sub todo의 deleted_at 필드를 현재 시간으로 업데이트합니다.
        - deleted_at 필드가 null이 아닌 경우 이미 삭제된 sub todo입니다.
        """  # noqa: E501
        subtodo_id = request.data.get("subtodo_id")
        try:
            sub_todo = SubTodo.objects.get_with_id(id=subtodo_id)
            SubTodo.objects.delete_instance(sub_todo)
        except SubTodo.DoesNotExist:
            return Response(
                {"error": "SubTodo not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "subtodo_id": sub_todo.id,
                "message": "SubTodo deleted successfully",
            },
            status=status.HTTP_200_OK,
        )


class CategoryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Category"],
        request_body=CategorySerializer,
        operation_summary="Create a category",
        responses={201: CategorySerializer},
    )
    def post(self, request):
        """
        - 이 함수는 category를 생성하는 함수입니다.
        - 입력 : user_id, title, color
        - title은 1자 이상 50자 이하여야합니다.
        - color는 7자여야합니다.
        """
        data = request.data

        serializer = CategorySerializer(
            context={"request": request}, data=data
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        tags=["Category"],
        request_body=SwaggerCategoryPatchSerializer,
        operation_summary="Update a category",
        responses={200: CategorySerializer},
    )
    def patch(self, request):
        """
        - 이 함수는 category를 수정하는 함수입니다.
        - 입력 : category_id, 수정 내용
        - 수정 내용은 title, color 중 하나 이상이어야 합니다.
        - order 의 경우 아래와 같이 수신됨
            "order" : {
                "prev_id" : 1,
                "next_id" : 3,
                "updated_order" : "0|asdf:"
            }
        """
        category_id = request.data.get("category_id")
        if "user_id" in request.data:
            return Response(
                {"error": "user_id cannot be updated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            category = Category.objects.get(
                id=category_id, deleted_at__isnull=True
            )
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if "order" in request.data:
            nested_order = request.data.get("order")
            request.data["order"] = nested_order.get("updated_order")
            request.data["patch_order"] = nested_order

        serializer = CategorySerializer(
            context={"request": request},
            instance=category,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        tags=["Category"],
        manual_parameters=[
            openapi.Parameter(
                "user_id",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="user_id",
                required=True,
            )
        ],
        operation_summary="Get a category",
        responses={200: CategorySerializer},
    )
    def get(self, request):
        """
        - 이 함수는 category list를 불러오는 함수입니다.
        - 입력 : user_id(필수)
        - user_id에 해당하는 category list를 불러옵니다.
        """
        user_id = request.GET.get("user_id")
        if user_id is None:
            return Response(
                {"error": "user_id must be provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            categories = Category.objects.get_with_user_id(user_id=user_id)
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        responses={200: CategorySerializer},
    )
    def delete(self, request):
        """
        - 이 함수는 category를 삭제하는 함수입니다.
        - 입력 : category_id
        - category_id에 해당하는 category의 deleted_at 필드를 현재 시간으로 업데이트합니다.
        - deleted_at 필드가 null이 아닌 경우 이미 삭제된 category입니다.
        """  # noqa: E501
        category_id = request.data.get("category_id")
        try:
            category = Category.objects.get_with_id(id=category_id)
            Category.objects.delete_instance(category)
            return Response(
                {
                    "category_id": category.id,
                    "message": "Category deleted successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
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
        - 입력 :  user_id(필수)
        - order 의 순서로 정렬합니다.
        """
        user_id = request.GET.get("user_id")

        if user_id is None:
            return Response(
                {"error": "user_id must be provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            todos = Todo.objects.get_inbox(user_id=user_id)
        except Todo.DoesNotExist:
            return Response(
                {"error": "Inbox is Empty"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = GetTodoSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    def post(self, request):
        """
        - 이 함수는 sub todo를 추천하는 함수입니다.
        - 입력 : todo_id, additional_info(option)
        - todo_id에 해당하는 todo_id 의 Contents 를 바탕으로 sub todo를 추천합니다.
        - 결과로 나올 수 있는 값으로는 question, answer, invalid content 가 있습니다.
        - question 은 sub todo 를 나눌 때 필요한 정보가 부족한 경우입니다.
            따라서 추가적인 질문이 content 에 포함됩니다.
        - additional_info 의 형태는 다음과 같습니다.
            [
                {
                    "question" : "",
                    "answer" : ""
                },
                ...
            ]
        """  # noqa: E501
        todo_id = request.data.get("todo_id")
        user_id = request.data.get("user_id")
        additional_info = request.data.get("additional_info", None)

        try:
            todo = Todo.objects.get_with_id(id=todo_id)
            user_prompt = create_user_prompt(todo, additional_info)
            if additional_info:
                for info in additional_info:
                    try:
                        log_data = {
                            "todo_id": todo_id,
                            "user_id": user_id,
                            "question": info["question"],
                            "answer": info["answer"],
                        }
                        serializer = PromptQuestionSerializer(data=log_data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                    except Exception as e:
                        return Response(
                            {"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": get_planner_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                response_format={"type": "json_object"},
            )
            prompt = json.loads(completion.choices[0].message.content)
            if prompt["type"] == "invalid_content":
                injection_data = {
                    "injection_reason": prompt["thinking"],
                    "todo_id": todo_id,
                    "user_id": user_id,
                }
                injection_serializer = PromptInjectionSerializer(
                    data=injection_data
                )
                injection_serializer.is_valid(raise_exception=True)
                injection_serializer.save()
            elif prompt["type"] == "answer":
                for content in prompt["contents"]:
                    sub_todo_data = {
                        "content": content["content"],
                        "todo_id": todo_id,
                        "user_id": user_id,
                    }
                    sub_todo_serializer = GeneratedSubTodoSerializer(
                        data=sub_todo_data
                    )
                    sub_todo_serializer.is_valid(raise_exception=True)
                    sub_todo_serializer.save()

        except Todo.DoesNotExist:
            return Response(
                {"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            json.loads(completion.choices[0].message.content),
            status=status.HTTP_200_OK,
        )
