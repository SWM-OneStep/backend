from django.contrib import admin
from django.urls import path, include
from accounts.views import *

urlpatterns = [path("login/", LoginView.as_view())]
