# todos/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from todos.models import Todo
from accounts.models import User
from todos.serializers import TodoSerializer
import re
from django.utils import timezone

class TodoView(APIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

    def post(self, request):
        '''
        - 이 함수는 todo를 생성하는 함수입니다.
        - 입력 : user_id, start_date, deadline, content, category, parent_id
        - content 는 암호화 되어야 합니다.
        - deadline 은 항상 start_date 와 같은 날이거나 그 이후여야합니다
        - category는 #으로 시작하며 뒤에는 6자여야 합니다.
        - content는 1자 이상 50자 이하여야합니다.
        - user_id 는 user 테이블에 존재해야합니다.
        - parent_id는 todo 테이블에 이미 존재해야합니다.
        - parent_id가 없는 경우 null로 처리합니다.
        - parent_id는 자기 자신을 참조할 수 없습니다.

        구현해야할 내용
        - order 순서 정리
        - 암호화
        '''
        data = request.data
        serializer = TodoSerializer(data=data)
        # category = 6자리 hex 색상코드 형식
        if 'category' in data:
            if not re.match(r'^#[0-9A-Fa-f]{6}$', data['category']):
                return Response({"error": "category must be a valid hex color code."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({"id": serializer.instance.id}, status=status.HTTP_201_CREATED)
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        '''
        - 이 함수는 todo list를 불러오는 함수입니다.
        - 입력 :  user_id, start_date, end_date
        - start_date와 end_date가 없는 경우 user_id에 해당하는 모든 todo를 불러옵니다.
        - start_date와 end_date가 있는 경우 user_id에 해당하는 todo 중 start_date와 end_date 사이에 있는 todo를 불러옵니다.
        - order 의 순서로 정렬합니다.

        구현되어야 할 사항
        - order 및 depth 에 따른 정렬
        '''
        user_id = request.GET.get('user_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        if start_date and end_date:
            todos = Todo.objects.filter(
                deleted_at__isnull=True,
                user_id=user_id,
                start_date__gte=start_date,
                deadline__lte=end_date
            ).order_by('order')
        else:
            todos = Todo.objects.filter(
                deleted_at__isnull=True,
                user_id=user_id
            ).order_by('order')

        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        '''
        - 이 함수는 todo를 수정하는 함수입니다.
        - 입력 : user_id, todo_id, 수정 내용
        - 수정 내용은 content, category, start_date, deadline, parent_id 중 하나 이상이어야 합니다.
        '''
        user_id = request.data.get('user_id')
        todo_id = request.data.get('todo_id')
        update_fields = ['content', 'category', 'start_date', 'deadline', 'parent_id', 'is_completed', 'order']
        update_data = {field: (request.data[field] if request.data[field] != '' else None) for field in update_fields if field in request.data}
        if not user_id or not todo_id:
            return Response({"error": "user_id and todo_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        if not update_data:
            return Response({"error": "At least one of content, category, start_date, deadline, or parent_id must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            todo = Todo.objects.get(id=todo_id, user_id=user_id, deleted_at__isnull=True)
        except Todo.DoesNotExist:
            return Response({"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND)

        for key, value in update_data.items():
            setattr(todo, key, value)

        todo.save()

        serializer = TodoSerializer(todo)
        # return Response({"todo_id": todo.id}, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)



    def delete(self, request):
        '''
        - 이 함수는 todo를 삭제하는 함수입니다.
        - 입력 : user_id, todo_id
        - todo_id에 해당하는 todo의 deleted_at 필드를 현재 시간으로 업데이트합니다.
        - deleted_at 필드가 null이 아닌 경우 이미 삭제된 todo입니다.
        '''
        user_id = request.data.get('user_id')
        todo_id = request.data.get('todo_id')

        if not user_id or not todo_id:
            return Response({"error": "user_id and todo_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            todo = Todo.objects.get(id=todo_id, user_id=user_id)
        except Todo.DoesNotExist:
            return Response({"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND)

        if todo.deleted_at is not None:
            return Response({"error": "Todo already deleted"}, status=status.HTTP_400_BAD_REQUEST)

        todo.deleted_at = timezone.now()
        todo.save()

        return Response({"todo_id": todo.id, "message": "Todo deleted successfully"}, status=status.HTTP_200_OK)