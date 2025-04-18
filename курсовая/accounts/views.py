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

User = get_user_model()
logger = logging.getLogger(__name__)

# Добавляем функцию anonymous_required
def anonymous_required(user):
    return not user.is_authenticated

def welcome_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'accounts/welcome.html')

@login_required
def home_view(request):
    return render(request, 'accounts/home.html', {'accounts': request.user})

def send_verification_email(email, verification_code):
    """
    Отправляет код верификации на email или выводит в консоль в зависимости от DEBUG_EMAIL_MODE
    """
    if DEBUG_EMAIL_MODE:
        logger.debug(f'DEBUG_EMAIL_MODE: Код верификации для {email}: {verification_code}')
        return True

    try:
        subject = 'Код верификации для ХабитТрекер'
        message = f'Ваш код верификации: {verification_code} (действителен 5 минут)'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        html_message = f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #4f46e5;">Подтверждение входа в ХабитТрекер</h2>
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

        if result == 1:
            logger.info(f'Письмо с кодом верификации успешно отправлено на {email}')
            return True
        else:
            logger.error(f'Не удалось отправить письмо на {email}. Результат: {result}')
            return False

    except Exception as e:
        logger.error(f'Ошибка отправки письма на {email}: {str(e)}', exc_info=True)
        return False

def generate_verification_code():
    """Генерирует 6-значный код верификации"""
    return str(random.randint(100000, 999999))

# Заменяем dashboard на home в декораторе
@user_passes_test(anonymous_required, login_url='home')
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.verification_code = generate_verification_code()
            user.verification_code_sent_at = timezone.now()
            user.save()

            # Логируем попытку отправки кода
            logger.info(f"Попытка отправки кода верификации для нового пользователя {user.email}")

            if send_verification_email(user.email, user.verification_code):
                request.session['user_id'] = user.id
                messages.info(request, 'На вашу почту отправлен код подтверждения.')
                return redirect('verify')
            else:
                messages.error(request, 'Не удалось отправить код подтверждения. Пожалуйста, попробуйте позже.')
                logger.error(f"Не удалось отправить код верификации для пользователя {user.email}")
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

                logger.info(f"Попытка отправки кода верификации для пользователя {user.email}")

                if send_verification_email(user.email, user.verification_code):
                    request.session['user_id'] = user.id
                    return redirect('verify')
                else:
                    messages.error(request, 'Не удалось отправить код подтверждения. Пожалуйста, попробуйте позже.')
                    logger.error(f"Не удалось отправить код верификации для пользователя {user.email}")
                    return redirect('login')
            else:
                logger.warning(f"Неудачная попытка входа для пользователя {username}")
                messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def resend_code(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Сессия истекла. Пожалуйста, войдите снова.')
        logger.warning("Попытка повторной отправки кода без user_id в сессии")
        return redirect('login')

    try:
        user = get_object_or_404(User, id=user_id)
        new_code = generate_verification_code()
        user.verification_code = new_code
        user.verification_attempts = 0
        user.verification_code_sent_at = timezone.now()
        user.save()

        logger.info(f"Повторная отправка кода верификации для пользователя {user.email}")

        if send_verification_email(user.email, new_code):
            messages.success(request, 'Новый код отправлен на вашу почту.')
            return redirect('verify')
        else:
            messages.error(request, 'Не удалось отправить код подтверждения. Пожалуйста, попробуйте позже.')
            logger.error(f"Не удалось отправить повторный код верификации для пользователя {user.email}")
            return redirect('verify')

    except Exception as e:
        logger.error(f'Ошибка при повторной отправке кода: {str(e)}', exc_info=True)
        messages.error(request, 'Произошла ошибка. Пожалуйста, попробуйте снова.')
        return redirect('login')


@user_passes_test(anonymous_required, login_url='home')
def verify_view(request):
    user_id = request.session.get('user_id')
    print(f"DEBUG: user_id from session: {user_id}")  # Добавлено
    if not user_id:
        messages.error(request, 'Сессия истекла. Пожалуйста, войдите снова.')
        logger.error("Нет user_id в сессии при попытке верификации")
        return redirect('login')

    try:
        user = get_object_or_404(User, id=user_id)
        logger.info(f"Начало верификации для пользователя {user.email}, код: {user.verification_code}")
        print(f"DEBUG: Found user: {user.email}")  # Добавлено
        print(f"DEBUG: Verification code: {user.verification_code}")  # Добавлено
        now = timezone.now()
        code_expired = (now - user.verification_code_sent_at) > timedelta(
            minutes=5) if user.verification_code_sent_at else True

        if code_expired or user.verification_attempts >= 3:
            logger.warning(f"Код истек или превышены попытки для пользователя {user.email}")
            user.verification_code = None
            user.save()
            code_expired = True

        if request.method == 'POST':
            form = VerificationForm(request.POST)
            if form.is_valid():
                code = form.cleaned_data['verification_code']
                logger.info(f"Попытка верификации с кодом: {code} (ожидается: {user.verification_code})")

                if code_expired:
                    logger.warning("Попытка использовать просроченный код")
                    return render(request, 'accounts/verify.html', {
                        'form': form,
                        'remaining_attempts': 0,
                        'code_expired': True,
                        'error_message': 'Код недействителен. Запросите новый код.'
                    })

                if user.verification_code == code:
                    logger.info("Код верификации совпадает")
                    user.reset_verification_attempts()
                    login(request, user)
                    del request.session['user_id']
                    return redirect('home')
                else:
                    user.verification_attempts += 1
                    user.save()
                    remaining_attempts = 3 - user.verification_attempts
                    logger.warning(f"Неверный код верификации. Осталось попыток: {remaining_attempts}")

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
                logger.warning("Невалидная форма верификации")
                return render(request, 'accounts/verify.html', {
                    'form': form,
                    'remaining_attempts': 3 - user.verification_attempts,
                    'code_expired': code_expired
                })
        else:
            form = VerificationForm()
            logger.info(f"Отображение формы верификации, код: {user.verification_code}")
            return render(request, 'accounts/verify.html', {
                'form': form,
                'remaining_attempts': 3 - user.verification_attempts if not code_expired else 0,
                'code_expired': code_expired
            })

    except Exception as e:
        logger.error(f'Ошибка при верификации: {str(e)}', exc_info=True)
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

                logger.info(f"Попытка отправки кода сброса пароля для {email}")

                if send_verification_email(email, verification_code):
                    request.session['reset_user_id'] = user.id
                    messages.success(request, 'Код подтверждения отправлен на вашу почту.')
                    return redirect('reset_password')
                else:
                    messages.error(request, 'Не удалось отправить код подтверждения. Пожалуйста, попробуйте позже.')
                    logger.error(f"Не удалось отправить код сброса пароля для {email}")
                    return redirect('forgot_password')
            else:
                logger.warning(f"Попытка сброса пароля для несуществующего email: {email}")
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

    return render(request, 'accounts/edit_profile.html', {'form': form})

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