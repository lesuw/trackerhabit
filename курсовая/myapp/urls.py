from django.urls import path, re_path
from . import views

urlpatterns = [
    path('user-<int:id>/', views.home, name ='users_index'),
    re_path(r'(user-\d)?\/$', views.home, name ='users_index'),
    ]