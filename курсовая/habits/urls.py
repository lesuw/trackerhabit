from django.urls import path, re_path
from . import views

urlpatterns = [
    path('habits/', views.add_habits, name='habits'),

    path('notes/', views.notes, name='notes'),
    path('edit/<int:pk>/', views.edit_note, name='edit_note'),
    path('delete/<int:pk>/', views.delete_note, name='delete_note'),
]