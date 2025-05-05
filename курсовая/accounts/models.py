from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.db import models
import random

def user_avatar_path(instance, filename):
    return f'user_{instance.id}/avatar/{filename}'

class User(AbstractUser):
    email = models.EmailField(unique=True, validators=[validate_email])
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_attempts = models.IntegerField(default=0)
    verification_code_sent_at = models.DateTimeField(blank=True, null=True)
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        blank=True,
        null=True,
        verbose_name='Аватар',
        default='images/default_avatar.png'
    )

    def generate_verification_code(self):
        return str(random.randint(100000, 999999))

    def reset_verification_attempts(self):
        self.verification_code = None
        self.verification_attempts = 0
        self.verification_code_sent_at = None
        self.save()



class Achievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    icon = models.CharField(max_length=50, verbose_name='Иконка (эмодзи)')
    achieved_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата получения')
    is_unlocked = models.BooleanField(default=False, verbose_name='Разблокировано')

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'
        ordering = ['-achieved_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"