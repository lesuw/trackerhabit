from django.db import models
from django.contrib.auth.models import User
from accounts.models import User

class Habit(models.Model):
    CATEGORY_CHOICES = [
        ('health', 'Здоровье'),
        ('productivity', 'Продуктивность'),
        ('learning', 'Обучение'),
        ('relationships', 'Отношения'),
        ('finance', 'Финансы'),
    ]

    COLOR_CHOICES = [
        ('bg-red-100 text-red-800', 'Красный'),
        ('bg-blue-100 text-blue-800', 'Синий'),
        ('bg-green-100 text-green-800', 'Зеленый'),
        ('bg-yellow-100 text-yellow-800', 'Желтый'),
        ('bg-purple-100 text-purple-800', 'Фиолетовый'),
        ('bg-pink-100 text-pink-800', 'Розовый'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    days_goal = models.PositiveIntegerField(default=30)
    color_class = models.CharField(max_length=50, choices=COLOR_CHOICES, default='bg-gray-100 text-gray-800')
    reminder = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class HabitSchedule(models.Model):
    DAY_CHOICES = [
        (0, 'Воскресенье'),
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
    ]

    habit = models.ForeignKey(Habit, related_name='schedule', on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAY_CHOICES)

    class Meta:
        unique_together = ('habit', 'day_of_week')

    def __str__(self):
        return f"{self.habit.name} - {self.get_day_of_week_display()}"