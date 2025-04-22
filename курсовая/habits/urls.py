from django.urls import path
from . import views

urlpatterns = [
    path('habits/', views.habits_page, name='habits_page'),  # Страница с привычками
    path('habits/save/', views.save_habit, name='save_habit'),
    path('habits/get_all/', views.get_all_habits, name='get_all_habits'),
    path('habits/get_by_day/', views.get_habits_by_day, name='get_habits_by_day'),

    # API эндпоинты
    path('api/habits/', views.get_habits, name='get_habits'),  # Все привычки пользователя
    path('api/habits/day/', views.get_habits_for_day, name='get_habits_for_day'),  # Привычки по дню недели
    path('api/habits/add/', views.add_habit, name='add_habit'),  # Создание привычки
    path('api/habits/<int:pk>/', views.get_habit, name='get_habit'),  # Получить конкретную привычку
    path('api/habits/<int:pk>/update/', views.update_habit, name='update_habit'),  # Обновление
    path('api/habits/<int:pk>/delete/', views.delete_habit, name='delete_habit'),  # Удаление
    path('api/habits/<int:pk>/track/', views.track_habit, name='track_habit'),  # Отслеживание выполнения
]
