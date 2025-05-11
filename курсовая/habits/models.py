# models.py
from django.db import models
from accounts.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

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

    def get_current_streak(self):
        """Возвращает текущую серию последовательных выполненных дней (исправленная версия)"""
        today = timezone.now().date()
        completions = self.completions.filter(
            date__lte=today
        ).order_by('-date')

        streak = 0
        prev_date = None

        for completion in completions:
            if prev_date is None:
                # Первая запись - проверяем что это сегодня или вчера
                if completion.date == today:
                    streak = 1
                    prev_date = completion.date
                elif (today - completion.date).days == 1:
                    streak = 1
                    prev_date = completion.date
                else:
                    break
            else:
                if (prev_date - completion.date).days == 1:
                    streak += 1
                    prev_date = completion.date
                else:
                    break

        return streak

    def get_longest_streak(self):
        """Исправленная версия для подсчета самой длинной серии"""
        completions = list(self.completions.order_by('date'))
        if not completions:
            return 0

        longest = current = 1

        for i in range(1, len(completions)):
            if (completions[i].date - completions[i-1].date).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1

        return longest

    def get_completion_rate(self):
        """Процент выполнения от цели"""
        total_completions = self.completions.count()
        return min(100, int((total_completions / self.days_goal) * 100))

    def is_completed_today(self):
        """Проверяет, выполнена ли привычка сегодня"""
        today = timezone.now().date()
        return self.completions.filter(date=today).exists()

    def is_completed_on(self, date):
        """Проверка, выполнена ли привычка в указанный день"""
        return self.completions.filter(date=date).exists()

    def mark_as_completed(self):
        """Отмечает привычку как выполненную на сегодня"""
        today = timezone.now().date()

        if self.is_completed_today():
            raise ValidationError("Эта привычка уже выполнена сегодня")

        HabitCompletion.objects.create(habit=self, date=today)

    def is_completed_on_current_date(self, date):
        """Проверяет, выполнена ли привычка в указанную дату"""
        return self.completions.filter(date=date).exists()

    def get_completion_days(self):
        """Возвращает список дней с момента создания привычки до days_goal дней вперед"""
        from datetime import timedelta

        days_to_show = self.days_goal
        start_date = self.created_at.date()
        end_date = start_date + timedelta(days=days_to_show - 1)

        # Создаем список всех дней в периоде
        date_list = [start_date + timedelta(days=x) for x in range(days_to_show)]

        # Получаем выполненные дни
        completed_dates = set(
            self.completions.filter(
                date__gte=start_date,
                date__lte=end_date,
                completed=True
            ).values_list('date', flat=True)
        )

        # Формируем результат
        return [{
            'date': date,
            'completed': date in completed_dates
        } for date in date_list]


class HabitSchedule(models.Model):
    DAY_CHOICES = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]

    habit = models.ForeignKey(Habit, related_name='schedule', on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAY_CHOICES)

    class Meta:
        unique_together = ('habit', 'day_of_week')

    def __str__(self):
        return f"{self.habit.name} - {self.get_day_of_week_display()}"

# models.py
class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
    date = models.DateField()
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('habit', 'date')
        constraints = [
            models.CheckConstraint(
                check=models.Q(date__lte=timezone.now().date()),
                name='date_cannot_be_in_future'
            )
        ]

    def __str__(self):
        return f"{self.habit.name} - {self.date} ({'Completed' if self.completed else 'Not completed'})"

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


