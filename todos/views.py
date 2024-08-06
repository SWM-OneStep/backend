# todos/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Prefetch, Q, Count
from todos.lexorank import LexoRank

from todos.models import Todo, SubTodo, Category
from todos.serializers import TodoSerializer, GetTodoSerializer, SubTodoSerializer, CategorySerializer
from todos.swagger_serializers import SwaggerTodoPatchSerializer, SwaggerSubTodoPatchSerializer, SwaggerCategoryPatchSerializer
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated, AllowAny

def validate_order(prev, next, updated):
    updated_lexo = LexoRank(updated)
    if prev is None and next is None:
        return True
    if prev is None:
        next_lexo = LexoRank(next)
        if next_lexo.compare_to(updated_lexo) <= 0:
            return False
    elif next is None:
        prev_lexo = LexoRank(prev)
        if prev_lexo.compare_to(updated_lexo) >= 0:
            return False
    else:
        prev_lexo = LexoRank(prev)
        next_lexo = LexoRank(next)
        if prev_lexo.compare_to(updated_lexo) >= 0 or next_lexo.compare_to(updated_lexo) <= 0:
            return False
    return True

class TodoView(APIView):
    permission_classes = [AllowAny]
    queryset = Todo.objects.all()

    @swagger_auto_schema(tags=['Todo'], request_body=TodoSerializer, operation_summary='Create a todo', responses={201: TodoSerializer})
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

        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                return Response({"error": "start_date must be before end_date"}, status=status.HTTP_400_BAD_REQUEST)
        
        # validate order
        last_todo = Todo.objects.filter(user_id=data['user_id'], deleted_at__isnull=True).order_by('-order').first()
        if last_todo is not None:
            last_order = last_todo.order
            if validate_order(prev=last_order, next=None, updated=data['order']) is False:  
                    return Response({"error": "Invalid order"}, status=status.HTTP_400_BAD_REQUEST)
        # category_id validation
        serializer = TodoSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(tags=['Todo'],manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='user_id', required=True),
        openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='start_date', required=False),
        openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='end_date', required=False)
    ],operation_summary='Get a todo', responses={200: GetTodoSerializer})
    def get(self, request):
        '''
        - 이 함수는 daily todo list를 불러오는 함수입니다.
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
        try:   
            if start_date is not None and end_date is not None: # start_date and end_date are not None
                todos = Todo.objects.get_daily_with_date(user_id=user_id, start_date=start_date, end_date=end_date)
            else: # start_date and end_date are None
                todos = Todo.objects.get_with_user_id(user_id=user_id).order_by('order')
        except Todo.DoesNotExist:
            return Response({"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = GetTodoSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(tags=['Todo'], request_body=SwaggerTodoPatchSerializer, operation_summary='Update a todo', responses={200: TodoSerializer})
    def patch(self, request):
        '''
        - 이 함수는 todo를 수정하는 함수입니다.
        - 입력 : todo_id, 수정 내용
        - 수정 내용은 content, category, start_date, end_date 중 하나 이상이어야 합니다.
        - order 의 경우 아래와 같이 제시된다.
            "order" : {
                "prev_id" : 1,
                "next_id" : 3,
                "updated_order" : "0|asdf:"
            }
        '''
        todo_id = request.data.get('todo_id')
        update_fields = ['content', 'category_id', 'start_date', 'end_date', 'is_completed']
        update_data = {field: request.data.get(field) for field in update_fields if field in request.data}
        
        if not update_data:
            return Response({"error": "At least one of content, category_id, start_date, end_date, is_completed must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        if 'user_id' in request.data:
            return Response({"error": "user_id cannot be updated"}, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get('start_date') and request.data.get('end_date') and update_data['start_date'] > update_data['end_date']:
            return Response({"error": "start_date must be before end_date"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            todo = Todo.objects.get(id=todo_id, deleted_at__isnull=True)
        except Todo.DoesNotExist:
            return Response({"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # validate order
        if request.data.get('order'):
            order_data = request.data.get('order')
            prev_id = order_data.get('prev_id')
            next_id = order_data.get('next_id')
            updated_order = order_data.get('updated_order')
            prev = None
            next = None
            if prev_id:
                prev = Todo.objects.filter(id=prev_id, deleted_at__isnull=True).first().order
            if next_id:
                next = Todo.objects.filter(id=next_id, deleted_at__isnull=True).first().order
            if validate_order(prev=prev, next=next, updated=updated_order) is False:
                return Response({"error": "Invalid order"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                update_data['order'] = updated_order
        
        serializer = TodoSerializer(todo, data=update_data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(tags=['Todo'], request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT, 
    properties={
        'todo_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='todo_id'),
    }), operation_summary='Delete a todo', responses={200: TodoSerializer})
    def delete(self, request):
        '''
        - 이 함수는 todo를 삭제하는 함수입니다.
        - 입력 : todo_id
        - todo_id에 해당하는 todo의 deleted_at 필드를 현재 시간으로 업데이트합니다.
        - deleted_at 필드가 null이 아닌 경우 이미 삭제된 todo입니다.
        - 해당 todo 에 속한 subtodo 도 전부 delete 를 해야함
        '''
        todo_id = request.data.get('todo_id')

        try:
            todo = Todo.objects.get_with_id(id=todo_id)
            subtodos = SubTodo.objects.get_subtodos(todo.id)
            SubTodo.objects.delete_many(subtodos)
            Todo.objects.delete_instance(todo)
        except Todo.DoesNotExist:
            return Response({"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e: 
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"todo_id": todo.id, "message": "Todo deleted successfully"}, status=status.HTTP_200_OK)
    

class SubTodoView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(tags=['SubTodo'], request_body=SubTodoSerializer(many=True), operation_summary='Create a subtodo', responses={201: SubTodoSerializer})
    def post(self, request):
        '''
        - 이 함수는 sub todo를 생성하는 함수입니다.
        - 입력 : todo, date, content, order
        - subtodo 는 리스트에 여러 객체가 들어간 형태를 가집니다.
        - content 는 암호화 되어야 합니다(// 미정)
        - date 는 parent의 start_date와 end_date의 사이여야 합니다.
        '''
        data = request.data

        for subtodo_data in data:
            # validate order
            last_subtodo = SubTodo.objects.filter(todo=subtodo_data['todo'], deleted_at__isnull=True).order_by('-order').first()
            if last_subtodo:
                last_order = last_subtodo.order
                if validate_order(prev=last_order, next=None, updated=subtodo_data['order']) is False:
                    return Response({"error": "Invalid order"}, status=status.HTTP_400_BAD_REQUEST)
            # # date validation 수정할 것 
            # todo = Todo.objects.get_with_id(id=data[0]['todo'])
            # if subtodo_data['date'] is not None:
            #     if todo.start_date is not None and todo.end_date is not None:
            #         subtodo_date = timezone.datetime.strptime(subtodo_data['date'], "%Y-%m-%d").date()
            #         if not (todo.start_date <= subtodo_date <= todo.end_date):
            #             return Response({"error": "Subtodo date must be between start_date and end_date of parent todo"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SubTodoSerializer(data=data, many=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(tags=['SubTodo'],manual_parameters=[
        openapi.Parameter('todo_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='todo_id', required=True)
    ],operation_summary='Get a subtodo', responses={200: SubTodoSerializer})
    def get(self, request):
        '''
        - 이 함수는 sub todo list를 불러오는 함수입니다.
        - 입력 : todo_id
        - parent_id에 해당하는 sub todo list를 불러옵니다.
        '''
        todo_id = request.GET.get('todo_id')
        try:
            sub_todos = SubTodo.objects.get_subtodos(todo_id= todo_id)
        except SubTodo.DoesNotExist:
            return Response({"error": "SubTodo not found"}, status=status.HTTP_404_NOT_FOUND)
    
        serializer = SubTodoSerializer(sub_todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @swagger_auto_schema(tags=['SubTodo'], request_body=SwaggerSubTodoPatchSerializer, operation_summary='Update a subtodo', responses={200: SubTodoSerializer})
    def patch(self, request):
        '''
        - 이 함수는 sub todo를 수정하는 함수입니다.
        - 입력 : subtodo_id, 수정 내용
        - 수정 내용은 content, date, parent_id 중 하나 이상이어야 합니다.
        - order 의 경우 아래와 같이 수신됨
            "order" : {
                "prev_id" : 1,
                "next_id" : 3,
                "updated_order" : "0|asdf:"
            }
        '''
        subtodo_id = request.data.get('subtodo_id')
        update_fields = ['content', 'date', 'is_completed', 'todo']
        update_data = {field: request.data.get(field) for field in update_fields if field in request.data}
        
        if not update_data:
            return Response({"error": "At least one of content, date, or parent_id must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        if 'user_id' in request.data:
            return Response({"error": "user_id cannot be updated"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            sub_todo = SubTodo.objects.get(id=subtodo_id, deleted_at__isnull=True)
        except SubTodo.DoesNotExist:
            return Response({"error": "SubTodo not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # validate order
        if request.data.get('order'):
            order_data = request.data.get('order')
            prev_id = order_data.get('prev_id')
            next_id = order_data.get('next_id')
            updated_order = order_data.get('updated_order')
            prev = None
            next = None
            if prev_id:
                prev = SubTodo.objects.filter(id=prev_id, deleted_at__isnull=True).first().order
            if next_id:
                next = SubTodo.objects.filter(id=next_id, deleted_at__isnull=True).first().order
            if validate_order(prev=prev, next=next, updated=updated_order) is False:
                return Response({"error": "Invalid order"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                update_data['order'] = updated_order
        # if request.data.get('date'): # date validation 나중에 수정할 것 
        #     todo_id = SubTodo.objects.get_with_id(id=subtodo_id).todo
        #     print("todo_id: ", todo_id)
        #     todo = Todo.objects.get_with_id(id=todo_id)
        #     subtodo_date = timezone.datetime.strptime(update_data['date'], "%Y-%m-%d").date()
        #     if not (todo.start_date <= subtodo_date <= todo.end_date):
        #         return Response({"error": "Subtodo date must be between start_date and end_date of parent todo"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SubTodoSerializer(sub_todo, data=update_data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['SubTodo'],request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT, 
    properties={
        'subtodo_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='subtodo_id'),
    }),operation_summary='Delete a subtodo', responses={200: SubTodoSerializer})
    def delete(self, request):
        '''
        - 이 함수는 sub todo를 삭제하는 함수입니다.
        - 입력 : subtodo_id
        - subtodo_id에 해당하는 sub todo의 deleted_at 필드를 현재 시간으로 업데이트합니다.
        - deleted_at 필드가 null이 아닌 경우 이미 삭제된 sub todo입니다.
        '''
        subtodo_id = request.data.get('subtodo_id')
        print(subtodo_id)
        try:
            sub_todo = SubTodo.objects.get_with_id(id=subtodo_id)
            SubTodo.objects.delete_instance(sub_todo)
        except SubTodo.DoesNotExist:
            return Response({"error": "SubTodo not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"subtodo_id": sub_todo.id, "message": "SubTodo deleted successfully"}, status=status.HTTP_200_OK)
    
class CategoryView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(tags=['Category'], request_body=CategorySerializer, operation_summary='Create a category', responses={201: CategorySerializer})
    def post(self, request):
        '''
        - 이 함수는 category를 생성하는 함수입니다.
        - 입력 : user_id, title, color
        - title은 1자 이상 50자 이하여야합니다.
        - color는 7자여야합니다.
        '''
        data = request.data

        # validate order
        last_category = Category.objects.filter(user_id=data['user_id'], deleted_at__isnull=True).order_by('-order').first()
        if last_category is not None:
            last_order = last_category.order
            if validate_order(prev=last_order, next=None, updated=data['order']) is False:  
                    return Response({"error": "Invalid order"}, status=status.HTTP_400_BAD_REQUEST) 
            
        serializer = CategorySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(tags=['Category'], request_body=SwaggerCategoryPatchSerializer, operation_summary='Update a category', responses={200: CategorySerializer})
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
        
        # validate order
        if request.data.get('order'):
            order_data = request.data.get('order')
            prev_id = order_data.get('prev_id')
            next_id = order_data.get('next_id')
            updated_order = order_data.get('updated_order')
            prev = None
            next = None
            if prev_id:
                prev = Category.objects.filter(id=prev_id, deleted_at__isnull=True).first().order
            if next_id:
                next = Category.objects.filter(id=next_id, deleted_at__isnull=True).first().order
            if validate_order(prev=prev, next=next, updated=updated_order) is False:
                return Response({"error": "Invalid order"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                update_data['order'] = updated_order
        
        serializer = CategorySerializer(category, data=update_data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(tags=['Category'],manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='user_id', required=True)
    ],operation_summary='Get a category', responses={200: CategorySerializer})
    def get(self, request):
        '''
        - 이 함수는 category list를 불러오는 함수입니다.
        - 입력 : user_id(필수)
        - user_id에 해당하는 category list를 불러옵니다.
        '''
        user_id = request.GET.get('user_id')
        if user_id is None:
            return  Response({"error": "user_id must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            categories = Category.objects.get_with_user_id(user_id=user_id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(tags=['Category'], request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT, 
    properties={
        'category_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Category_id'),
    }),operation_summary='Delete a category', responses={200: CategorySerializer})
    def delete(self, request):
        '''
        - 이 함수는 category를 삭제하는 함수입니다.
        - 입력 : category_id
        - category_id에 해당하는 category의 deleted_at 필드를 현재 시간으로 업데이트합니다.
        - deleted_at 필드가 null이 아닌 경우 이미 삭제된 category입니다.
        '''
        category_id = request.data.get('category_id')
        try:
            category = Category.objects.get_with_id(id=category_id)
            Category.objects.delete_instance(category)
            return Response({"category_id": category.id, "message": "Category deleted successfully"}, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class InboxView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(tags=['InboxTodo'],manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='user_id', required=True),
    ],operation_summary='Get Inbox todo', responses={200: GetTodoSerializer})
    def get(self, request):
        '''
        - 이 함수는 daily todo list를 불러오는 함수입니다.
        - 입력 :  user_id(필수)
        - order 의 순서로 정렬합니다.
        '''
        user_id = request.GET.get('user_id')

        if user_id is None:
            return Response({"error": "user_id must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            todos = Todo.objects.get_inbox(user_id=user_id)
        except Todo.DoesNotExist:
            return Response({"error": "Inbox is Empty"}, status=status.HTTP_404_NOT_FOUND)
        serializer = GetTodoSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)