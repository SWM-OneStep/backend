# todos/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Prefetch

from todos.models import Todo, SubTodo, Category
from accounts.models import User
from todos.serializers import TodoSerializer, GetTodoSerializer, SubTodoSerializer, CategorySerializer, GetCategoryTodoSerializer
import re
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated, AllowAny

class TodoView(APIView):
    permission_classes = [AllowAny]
    queryset = Todo.objects.all()

    def post(self, request):
        '''
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
        '''
        data = request.data

        if data['start_date'] and data['end_date'] and data['start_date'] > data['end_date']:
            return Response({"error": "start_date must be before end_date"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TodoSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        '''
        - 이 함수는 today todo list를 불러오는 함수입니다.
        - 입력 :  user_id(필수), start_date, end_date
        - start_date와 end_date가 없는 경우 user_id에 해당하는 모든 todo를 불러옵니다.
        - start_date와 end_date가 있는 경우 user_id에 해당하는 todo 중 start_date와 end_date 사이에 있는 todo를 불러옵니다.
        - order 의 순서로 정렬합니다.

        형식 : 
        구현되어야 할 사항
        - order 및 depth 에 따른 정렬
        '''
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        user_id = request.GET.get('user_id')
        if user_id is None:
            return Response({"error": "user_id must be provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        if end_date ^ start_date: # start_date or end_date is None
            if start_date:
                todos = Todo.objects.filter(
                    user_id = user_id,
                    start_date__gte=start_date,
                    deleted_at__isnull=True
                ).order_by('order').prefetch_related(
                    Prefetch('subtodos', queryset=SubTodo.objects.filter(deleted_at__isnull=True).order_by('order'))
                )
                
            else:
                todos = Todo.objects.filter(
                    user_id = user_id,
                    end_date__lte=end_date,
                    deleted_at__isnull=True
                ).order_by('order').prefetch_related(
                    Prefetch('subtodos', queryset=SubTodo.objects.filter(deleted_at__isnull=True).order_by('order'))
                )
        elif start_date and end_date: # start_date and end_date are not None
            todos = Todo.objects.filter(
                user_id = user_id,
                start_date__gte=start_date,
                end_date__lte=end_date,
                deleted_at__isnull=True
            ).order_by('order').prefetch_related(
                Prefetch('subtodos', queryset=SubTodo.objects.filter(deleted_at__isnull=True).order_by('order'))
            )
        else: # start_date and end_date are None
            todos = Todo.objects.filter(user_id = user_id, deleted_at__isnull=True).order_by('order').prefetch_related(
                Prefetch('subtodos', queryset=SubTodo.objects.filter(deleted_at__isnull=True).order_by('order'))
            )

        serializer = GetTodoSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        '''
        - 이 함수는 todo를 수정하는 함수입니다.
        - 입력 : todo_id, 수정 내용
        - 수정 내용은 content, category, start_date, deadline, parent_id 중 하나 이상이어야 합니다.
        '''
        todo_id = request.data.get('todo_id')
        update_fields = ['content', 'category_id', 'start_date', 'end_date', 'is_completed', 'order']
        update_data = {field: request.data.get(field) for field in update_fields if field in request.data}
        if not update_data:
            return Response({"error": "At least one of content, category_id, start_date, end_date, or parent_id must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        if 'user_id' in request.data:
            return Response({"error": "user_id cannot be updated"}, status=status.HTTP_400_BAD_REQUEST)
        if update_data['start_date'] and update_data['end_date'] and update_data['start_date'] > update_data['end_date']:
            return Response({"error": "start_date must be before end_date"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            todo = Todo.objects.get(id=todo_id, deleted_at__isnull=True)
        except Todo.DoesNotExist:
            return Response({"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND)
        

        serializer = TodoSerializer(todo, data=update_data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request):
        '''
        - 이 함수는 todo를 삭제하는 함수입니다.
        - 입력 : todo_id
        - todo_id에 해당하는 todo의 deleted_at 필드를 현재 시간으로 업데이트합니다.
        - deleted_at 필드가 null이 아닌 경우 이미 삭제된 todo입니다.
        '''
        todo_id = request.data.get('todo_id')

        try:
            todo = Todo.objects.get(id=todo_id, deleted_at__isnull=True)
        except Todo.DoesNotExist:
            return Response({"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND)

        if todo.deleted_at is not None:
            return Response({"error": "Todo already deleted"}, status=status.HTTP_400_BAD_REQUEST)

        todo.deleted_at = timezone.now()
        todo.save()

        return Response({"todo_id": todo.id, "message": "Todo deleted successfully"}, status=status.HTTP_200_OK)
    

class SubTodoView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        '''
        - 이 함수는 sub todo를 생성하는 함수입니다.
        - 입력 : user_id, todo, date, content, category
        - content 는 암호화 되어야 합니다(// 미정)
        - date 는 parent의 start_date와 end_date의 사이여야 합니다.
        '''
        data = request.data

        serializer = SubTodoSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

    def get(self, request):
        '''
        - 이 함수는 sub todo list를 불러오는 함수입니다.
        - 입력 : subtodo_id
        - parent_id에 해당하는 sub todo list를 불러옵니다.
        '''
        subtodo_id = request.GET.get('subtodo_id')
        try:
            sub_todo = SubTodo.objects.get(id=subtodo_id, deleted_at__isnull=True)
        except SubTodo.DoesNotExist:
            return Response({"error": "SubTodo not found"}, status=status.HTTP_404_NOT_FOUND)
    
        serializer = SubTodoSerializer(sub_todo)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        '''
        - 이 함수는 sub todo를 수정하는 함수입니다.
        - 입력 : subtodo_id, 수정 내용
        - 수정 내용은 content, date, parent_id 중 하나 이상이어야 합니다.
        '''
        subtodo_id = request.data.get('subtodo_id')
        update_fields = ['content', 'date', 'is_completed', 'order']
        update_data = {field: request.data.get(field) for field in update_fields if field in request.data}
        
        if not update_data:
            return Response({"error": "At least one of content, date, or parent_id must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        if 'user_id' in request.data:
            return Response({"error": "user_id cannot be updated"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            sub_todo = SubTodo.objects.get(id=subtodo_id, deleted_at__isnull=True)
        except SubTodo.DoesNotExist:
            return Response({"error": "SubTodo not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SubTodoSerializer(sub_todo, data=update_data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        '''
        - 이 함수는 sub todo를 삭제하는 함수입니다.
        - 입력 : subtodo_id
        - subtodo_id에 해당하는 sub todo의 deleted_at 필드를 현재 시간으로 업데이트합니다.
        - deleted_at 필드가 null이 아닌 경우 이미 삭제된 sub todo입니다.
        '''
        subtodo_id = request.data.get('subtodo_id')

        try:
            sub_todo = SubTodo.objects.get(id=subtodo_id, deleted_at__isnull=True)
        except SubTodo.DoesNotExist:
            return Response({"error": "SubTodo not found"}, status=status.HTTP_404_NOT_FOUND)

        if sub_todo.deleted_at is True:
            return Response({"error": "SubTodo already deleted"}, status=status.HTTP_400_BAD_REQUEST)

        sub_todo.deleted_at = timezone.now()
        sub_todo.save()

        return Response({"subtodo_id": sub_todo.id, "message": "SubTodo deleted successfully"}, status=status.HTTP_200_OK)
    
class CategoryView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        '''
        - 이 함수는 category를 생성하는 함수입니다.
        - 입력 : user_id, title, color
        - title은 1자 이상 50자 이하여야합니다.
        - color는 7자여야합니다.
        '''
        data = request.data
        serializer = CategorySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

    def patch(self, request):
        '''
        - 이 함수는 category를 수정하는 함수입니다.
        - 입력 : category_id, 수정 내용
        - 수정 내용은 title, color 중 하나 이상이어야 합니다.
        '''
        category_id = request.data.get('category_id')
        update_fields = ['title', 'color', 'order']
        update_data = {field: request.data.get(field) for field in update_fields if field in request.data}
        if not update_data:
            return Response({"error": "At least one of title or color must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        if 'user_id' in request.data:
            return Response({"error": "user_id cannot be updated"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            category = Category.objects.get(id=category_id, deleted_at__isnull=True)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(category, data=update_data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        '''
        - 이 함수는 category list를 불러오는 함수입니다.
        - 입력 : user_id(필수)
        - user_id에 해당하는 category list를 불러옵니다.
        '''
        user_id = request.GET.get('user_id')
        if user_id is None:
            return  Response({"error": "user_id must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        categories = Category.objects.filter(
            user_id=user_id,
            deleted_at__isnull=True
        )
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request):
        '''
        - 이 함수는 category를 삭제하는 함수입니다.
        - 입력 : category_id
        - category_id에 해당하는 category의 deleted_at 필드를 현재 시간으로 업데이트합니다.
        - deleted_at 필드가 null이 아닌 경우 이미 삭제된 category입니다.
        '''
        category_id = request.data.get('category_id')
        category = Category.objects.get(id=category_id, deleted_at__isnull=True)
        if category.deleted_at is not None:
            return Response({"error": "Category already deleted"}, status=status.HTTP_400_BAD_REQUEST)
        category.deleted_at = timezone.now()
        category.save()
        return Response({"category_id": category.id, "message": "Category deleted successfully"}, status=status.HTTP_200_OK)
    
class TodayTodoView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        '''
        - 이 함수는 today todo list를 불러오는 함수입니다.
        - 입력 :  user_id(필수), start_date, end_date
        - start_date와 end_date가 없는 경우 user_id에 해당하는 모든 todo를 불러옵니다.
        - start_date와 end_date가 있는 경우 user_id에 해당하는 todo 중 start_date와 end_date 사이에 있는 todo를 불러옵니다.
        - order 의 순서로 정렬합니다.
        '''
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        user_id = request.GET.get('user_id')

        if user_id is None:
            return Response({"error": "user_id must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        if start_date and end_date:
            todos = Category.objects.filter(
                user_id=user_id,
                todos__start_date__gte=start_date,
                todos__end_date__lte=end_date,
                deleted_at__isnull=True
            ).order_by('order').prefetch_related(
                Prefetch('todos', queryset=Todo.objects.filter(deleted_at__isnull=True).order_by('order').prefetch_related(
                    Prefetch('subtodos', queryset=SubTodo.objects.filter(deleted_at__isnull=True).order_by('order'))
                ))
            )
        else:
            todos = Category.objects.filter(
                user_id=user_id,
                deleted_at__isnull=True
            ).order_by('order').prefetch_related(
                Prefetch('todos', queryset=Todo.objects.filter(deleted_at__isnull=True).order_by('order').prefetch_related(
                    Prefetch('subtodos', queryset=SubTodo.objects.filter(deleted_at__isnull=True).order_by('order'))
                ))
            )
        
        serializer = GetCategoryTodoSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
'''
checklist
- today 뷰에서 삭제된 것이 안 보이도록 할 것 
- start_date와 end_date에 대해 체크할 것 (get 과 패치에 관해서 해결할 것)
'''