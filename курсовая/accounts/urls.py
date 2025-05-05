from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_view, name='welcome'),
    path('home/', views.home_view, name='home'),

    # Регистрация и вход
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify/', views.verify_view, name='verify'),
    path('resend-code/', views.resend_code, name='resend_code'),

    # Восстановление пароля
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),

    # Профиль пользователя
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete-avatar/', views.delete_avatar, name='delete_avatar'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('achievements/', views.achievements_view, name='achievements'),
]