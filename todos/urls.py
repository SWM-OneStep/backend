# todos/urls.py
from django.urls import path
from todos.views import *

urlpatterns = [
    path('', TodoView.as_view()),
    # path('<int:pk>/', views.todo_detail),
]