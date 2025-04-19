from django.urls import path, re_path
from . import views

urlpatterns = [
    path('habits/', views.add_habits, name='habits'),
]