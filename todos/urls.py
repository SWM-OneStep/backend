# todos/urls.py
from django.urls import path
from todos.views import *

urlpatterns = [
    path('todo/', TodoView.as_view(), name='todos'),
    path('sub/', SubTodoView.as_view(), name='subtodos'),
    path('category/', CategoryView.as_view(), name='category'),
    path('inbox/', InboxView.as_view(), name='inbox'),
    path('recommend/', RecommendSubTodo.as_view(), name='Recommend'),
]

