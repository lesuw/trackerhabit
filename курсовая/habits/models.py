# models.py
from django.db import models
from accounts.models import User

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