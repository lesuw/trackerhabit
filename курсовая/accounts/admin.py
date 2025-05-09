from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import User  # замените на вашу модель пользователя

admin.site.register(User, UserAdmin)