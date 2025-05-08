# models.py
from django.db import models
from accounts.models import User
from django.utils import timezone

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

class MoodEntry(models.Model):
    MOOD_CHOICES = [
        ('ecstatic', 'Отлично'),
        ('happy', 'Хорошо'),
        ('neutral', 'Нормально'),
        ('sad', 'Плохо'),
        ('angry', 'Ужасно'),
    ]

    MOOD_EMOJI_URLS = {
        'ecstatic': 'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f604.svg',
        'happy': 'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f642.svg',
        'neutral': 'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f610.svg',
        'sad': 'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f641.svg',
        'angry': 'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f620.svg',
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(null=True, blank=True)
    mood = models.CharField(max_length=10, choices=MOOD_CHOICES)
    notes = models.TextField()

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Mood Entries'

    def __str__(self):
        return f"{self.get_mood_display()} - {self.date.strftime('%d.%m.%Y')}"

    def save(self, *args, **kwargs):
        if self.pk:
            self.last_edited = timezone.now()
        super().save(*args, **kwargs)

    def get_emoji_url(self):
        return self.MOOD_EMOJI_URLS.get(self.mood, '')

    def get_mood_display(self):
        return dict(self.MOOD_CHOICES).get(self.mood, 'Неизвестно')


# models.py
class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
    date = models.DateField()
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('habit', 'date')

    def __str__(self):
        return f"{self.habit.name} - {self.date} ({'Completed' if self.completed else 'Not completed'})"