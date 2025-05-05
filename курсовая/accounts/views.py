import logging
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

import random

from django_project.settings import DEBUG_EMAIL_MODE
from .forms import (
    RegisterForm, LoginForm, VerificationForm,
    ResetPasswordForm, NewPasswordForm, UserEditForm,
    PasswordChangeForm
)
from .models import Achievement

User = get_user_model()

def anonymous_required(user):
    return not user.is_authenticated

def welcome_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'accounts/welcome.html')

@login_required
def home_view(request):
    tips = [
        "Пейте воду утром для бодрости",
        "Сделайте 5-минутную разминку перед работой",
        "Запишите цель на день и держите перед глазами",
        "Сформируйте привычку — начните с малого",
        "Ограничьте соцсети перед сном для лучшего сна",
        "Начните день с улыбки и сделайте его продуктивным"
    ]
    random_tip = random.choice(tips)

    # Получаем последние 3 разблокированных достижения
    recent_achievements = request.user.achievements.filter(is_unlocked=True).order_by('-achieved_at')[:3]

    return render(request, 'accounts/home.html', {
        'accounts': request.user,
        'random_tip': random_tip,
        'recent_achievements': recent_achievements
    })

def send_verification_email(email, verification_code):
    """
    Отправляет код верификации на email или выводит в консоль в зависимости от DEBUG_EMAIL_MODE
    """
    if DEBUG_EMAIL_MODE:
        print(f'DEBUG_EMAIL_MODE: Код верификации для {email}: {verification_code}')
        return True

    try:
        subject = 'Код верификации для HabitHub'
        message = f'Ваш код верификации: {verification_code} (действителен 5 минут)'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        html_message = f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #4f46e5;">Подтверждение входа в HabitHub</h2>
                <p>Ваш код верификации: <strong style="font-size: 1.2em;">{verification_code}</strong></p>
                <p>Код действителен в течение 5 минут.</p>
                <p style="margin-top: 30px; color: #6b7280;">Если вы не запрашивали этот код, проигнорируйте это письмо.</p>
            </div>
        '''

        result = send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
            html_message=html_message
        )

        return result == 1

    except Exception as e:
        print(f'Ошибка отправки письма на {email}: {str(e)}')
        return False

def generate_verification_code():
    """Генерирует 6-значный код верификации"""
    return str(random.randint(100000, 999999))

@user_passes_test(anonymous_required, login_url='home')
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.verification_code = generate_verification_code()
            user.verification_code_sent_at = timezone.now()
            user.save()

            if send_verification_email(user.email, user.verification_code):
                request.session['user_id'] = user.id
                messages.info(request, 'На вашу почту отправлен код подтверждения.')
                return redirect('verify')
            else:
                messages.error(request, 'Не удалось отправить код подтверждения. Пожалуйста, попробуйте позже.')
                return redirect('register')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

@user_passes_test(anonymous_required, login_url='home')
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                user.verification_code = generate_verification_code()
                user.verification_code_sent_at = timezone.now()
                user.save()

                if send_verification_email(user.email, user.verification_code):
                    request.session['user_id'] = user.id
                    return redirect('verify')
                else:
                    messages.error(request, 'Не удалось отправить код подтверждения. Пожалуйста, попробуйте позже.')
                    return redirect('login')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def resend_code(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Сессия истекла. Пожалуйста, войдите снова.')
        return redirect('login')

    try:
        user = get_object_or_404(User, id=user_id)
        new_code = generate_verification_code()
        user.verification_code = new_code
        user.verification_attempts = 0
        user.verification_code_sent_at = timezone.now()
        user.save()

        if send_verification_email(user.email, new_code):
            messages.success(request, 'Новый код отправлен на вашу почту.')
            return redirect('verify')
        else:
            messages.error(request, 'Не удалось отправить код подтверждения. Пожалуйста, попробуйте позже.')
            return redirect('verify')

    except Exception as e:
        messages.error(request, 'Произошла ошибка. Пожалуйста, попробуйте снова.')
        return redirect('login')

@user_passes_test(anonymous_required, login_url='home')
def verify_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Сессия истекла. Пожалуйста, войдите снова.')
        return redirect('login')

    try:
        user = get_object_or_404(User, id=user_id)
        now = timezone.now()
        code_expired = (now - user.verification_code_sent_at) > timedelta(
            minutes=5) if user.verification_code_sent_at else True

        if code_expired or user.verification_attempts >= 3:
            user.verification_code = None
            user.save()
            code_expired = True

        if request.method == 'POST':
            form = VerificationForm(request.POST)
            if form.is_valid():
                code = form.cleaned_data['verification_code']

                if code_expired:
                    return render(request, 'accounts/verify.html', {
                        'form': form,
                        'remaining_attempts': 0,
                        'code_expired': True,
                        'error_message': 'Код недействителен. Запросите новый код.'
                    })

                if user.verification_code == code:
                    user.reset_verification_attempts()
                    login(request, user)
                    del request.session['user_id']
                    return redirect('home')
                else:
                    user.verification_attempts += 1
                    user.save()
                    remaining_attempts = 3 - user.verification_attempts

                    if user.verification_attempts >= 3:
                        user.verification_code = None
                        user.save()
                        return render(request, 'accounts/verify.html', {
                            'form': form,
                            'remaining_attempts': 0,
                            'code_expired': True,
                            'error_message': 'Превышено количество попыток. Запросите новый код.'
                        })
                    else:
                        return render(request, 'accounts/verify.html', {
                            'form': form,
                            'remaining_attempts': remaining_attempts,
                            'error_message': f'Неверный код. Осталось попыток: {remaining_attempts}'
                        })
            else:
                return render(request, 'accounts/verify.html', {
                    'form': form,
                    'remaining_attempts': 3 - user.verification_attempts,
                    'code_expired': code_expired
                })
        else:
            form = VerificationForm()
            return render(request, 'accounts/verify.html', {
                'form': form,
                'remaining_attempts': 3 - user.verification_attempts if not code_expired else 0,
                'code_expired': code_expired
            })

    except Exception as e:
        messages.error(request, 'Произошла ошибка. Пожалуйста, попробуйте снова.')
        return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('home')

@user_passes_test(anonymous_required, login_url='home')
def forgot_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()

            if user:
                verification_code = generate_verification_code()
                user.verification_code = verification_code
                user.verification_code_sent_at = timezone.now()
                user.save()

                if send_verification_email(email, verification_code):
                    request.session['reset_user_id'] = user.id
                    messages.success(request, 'Код подтверждения отправлен на вашу почту.')
                    return redirect('reset_password')
                else:
                    messages.error(request, 'Не удалось отправить код подтверждения. Пожалуйста, попробуйте позже.')
                    return redirect('forgot_password')
            else:
                messages.error(request, 'Пользователь с таким email не найден.')
    else:
        form = ResetPasswordForm()

    return render(request, 'accounts/forgot_password.html', {'form': form})

@user_passes_test(anonymous_required, login_url='home')
def reset_password(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('forgot_password')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['verification_code']
            new_password = form.cleaned_data['new_password1']

            if user.verification_code == code:
                user.set_password(new_password)
                user.verification_code = None
                user.save()
                messages.success(request, 'Пароль успешно изменён! Теперь вы можете войти.')
                del request.session['reset_user_id']
                return redirect('login')
            else:
                form.add_error('verification_code', 'Неверный код подтверждения.')
    else:
        form = NewPasswordForm()

    return render(request, 'accounts/reset_password.html', {'form': form})

@login_required
def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('welcome')
    return render(request, 'accounts/profile.html', {'accounts': request.user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен.')
            return redirect('profile')
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form, 'accounts': request.user})

@login_required
def delete_avatar(request):
    if request.method == 'POST':
        user = request.user
        if user.avatar and user.avatar.name != 'avatars/default_avatar.png':
            user.avatar.delete()
        user.avatar = 'avatars/default_avatar.png'
        user.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid method'}, status=400)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password1']

            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Пароль успешно изменен.')
                return redirect('profile')
            else:
                form.add_error('old_password', 'Текущий пароль введен неверно.')
    else:
        form = PasswordChangeForm()

    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def achievements_view(request):
    # Стандартные достижения
    default_achievements = [
        {
            'title': 'Первый шаг',
            'description': 'Вы успешно зарегистрировались в системе!',
            'icon': '🎉',
            'condition': lambda user: True  # Всегда true для зарегистрированных
        },
        {
            'title': 'Стартовый рывок',
            'description': 'Выполнить привычку 5 раз подряд без пропусков',
            'icon': '🚀',
            'condition': lambda user: hasattr(user, 'habits') and user.habits.filter(streak__gte=1).exists()
        },
        {
            'title': 'Месяц мастерства',
            'description': 'Выполнять привычку 30 дней подряд без пропусков',
            'icon': '🏆',
            'condition': lambda user: hasattr(user, 'habits') and user.habits.filter(streak__gte=30).exists()
        },
        {
            'title': 'Легендарная серия',
            'description': '100 дней непрерывного выполнения привычки',
            'icon': '🌟',
            'condition': lambda user: hasattr(user, 'habits') and user.habits.filter(streak__gte=100).exists()
        },
        {
            'title': 'Мультитаскер',
            'description': 'Создать 5 разных привычек',
            'icon': '🌀',
            'condition': lambda user: hasattr(user, 'habits') and user.habits.count() >= 5
        },
        {
            'title': 'Перфекционист',
            'description': 'Выполнить привычку идеально 7 дней подряд',
            'icon': '✨',
            'condition': lambda user: hasattr(user, 'habits') and user.habits.filter(perfect_streak__gte=7).exists()
        },
        {
            'title': 'Неудержимый',
            'description': 'Выполнить привычку в выходной день',
            'icon': '💪',
            'condition': lambda user: hasattr(user, 'habits') and user.habits.filter(completed_on_weekend=True).exists()
        },

    ]

    # Проверяем и создаем достижения
    for achievement_data in default_achievements:
        try:
            if achievement_data['condition'](request.user):
                Achievement.objects.get_or_create(
                    user=request.user,
                    title=achievement_data['title'],
                    defaults={
                        'description': achievement_data['description'],
                        'icon': achievement_data['icon'],
                        'is_unlocked': True
                    }
                )
        except Exception as e:
            print(f"Ошибка при проверке достижения {achievement_data['title']}: {str(e)}")
            continue

    achievements = request.user.achievements.all().order_by('-achieved_at')
    unlocked_count = request.user.achievements.filter(is_unlocked=True).count()
    total_count = len(default_achievements)

    return render(request, 'accounts/achievements.html', {
        'achievements': achievements,
        'unlocked_count': unlocked_count,
        'total_count': total_count,
        'progress_percentage': (unlocked_count / total_count * 100) if total_count > 0 else 0
    })


@user_passes_test(anonymous_required, login_url='home')
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.verification_code = generate_verification_code()
            user.verification_code_sent_at = timezone.now()
            user.save()

            # Создаем достижение за регистрацию
            Achievement.objects.create(
                user=user,
                title='Первый шаг',
                description='Вы успешно зарегистрировались в системе!',
                icon='🎉',
                is_unlocked=True
            )

            if send_verification_email(user.email, user.verification_code):
                request.session['user_id'] = user.id
                messages.info(request, 'На вашу почту отправлен код подтверждения.')
                return redirect('verify')
            else:
                messages.error(request, 'Не удалось отправить код подтверждения. Пожалуйста, попробуйте позже.')
                return redirect('register')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    user = request.user
    achievements = user.achievements.all().order_by('-achieved_at')
    unlocked_count = achievements.filter(is_unlocked=True).count()
    total_achievements = 3  # Или ваш расчет общего количества возможных достижений
    progress_percentage = (unlocked_count / total_achievements * 100) if total_achievements > 0 else 0

    return render(request, 'accounts/profile.html', {
        'accounts': user,
        'achievements': achievements,
        'unlocked_count': unlocked_count,
        'total_achievements': total_achievements,
        'progress_percentage': progress_percentage
    })