from django.urls import path, re_path
from . import views

urlpatterns = [
    path('habits/', views.habits_page, name='habits'),
    path('habits/save/', views.save_habit, name='save_habit'),
    path('habits/get_all/', views.get_all_habits, name='get_all_habits'),
    path('habits/get_by_day/', views.get_habits_by_day, name='get_habits_by_day'),
    path('habits/delete/<int:id>/', views.delete_habit, name='delete_habit'),
    path('habits/update/<int:id>/', views.update_habit, name='update_habit'),
    path('habits/get/<int:id>/', views.get_habit, name='get_habit'),
    path('habits/update_schedule/', views.update_schedule, name='update_schedule'),



    path('notes/', views.notes, name='notes'),
    path('edit/<int:pk>/', views.edit_note, name='edit_note'),
    path('delete/<int:pk>/', views.delete_note, name='delete_note'),

    path('faq/', views.faq_page, name='faq'),

#Календарь
    path('calendar/', views.calendar_view, name='calendar'),
    path('day/<int:year>/<int:month>/<int:day>/', views.day_details, name='day_details'),
    path('api/toggle-completion/<int:habit_id>/', views.toggle_completion, name='toggle_completion'),
    path('add-to-calendar/', views.add_habit_to_calendar, name='add_habit_to_calendar'),

#трекер
    path('tracker/', views.habit_tracker, name='habit_tracker'),
    path('get_completion_days/', views.get_completion_days, name='get_completion_days'),
    path('mark-completion/', views.mark_habit_completion, name='mark_habit_completion'),

# API эндпоинты
#     path('api/habits/', views.get_habit, name='get_habits'),  # Все привычки пользователя
    path('api/habits/day/', views.get_habits_for_day, name='get_habits_for_day'),  # Привычки по дню недели
    path('api/habits/add/', views.add_habit, name='add_habit'),  # Создание привычки
      # Получить конкретную привычку  # Обновление
    # path('api/habits/<int:pk>/delete/', views.delete_habit, name='delete_habit'),  # Удаление
    path('api/habits/<int:pk>/track/', views.track_habit, name='track_habit'),  # Отслеживание выполнения
]
