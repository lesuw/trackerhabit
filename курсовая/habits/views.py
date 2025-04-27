from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from .models import MoodEntry
from .forms import MoodEntryForm
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from .models import Habit, HabitSchedule
from django.views.decorators.http import require_GET
import json


@login_required
def notes(request):
    # Фильтрация заметок
    entries = MoodEntry.objects.filter(user=request.user)

    # Применение фильтров
    mood_filter = request.GET.get('mood')
    date_filter = request.GET.get('date')

    if mood_filter:
        entries = entries.filter(mood=mood_filter)
    if date_filter:
        entries = entries.filter(date__date=date_filter)

    # Сортировка и пагинация
    entries = entries.order_by('-date')
    paginator = Paginator(entries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Обработка AJAX-запросов
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            return handle_note_ajax(request)
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    # Обычный GET-запрос
    return render(request, 'notes/notes.html', {
        'page_obj': page_obj,
        'mood_filter': mood_filter,
        'date_filter': date_filter,
    })


def handle_note_ajax(request):
    try:
        data = request.POST
        action = data.get('action')

        if action == 'add':
            form = MoodEntryForm(data)
            if form.is_valid():
                entry = form.save(commit=False)
                entry.user = request.user
                entry.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Заметка добавлена',
                    'note': serialize_note(entry)
                })
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            }, status=400)

        elif action == 'edit':
            entry_id = data.get('entry_id')
            entry = get_object_or_404(MoodEntry, id=entry_id, user=request.user)
            form = MoodEntryForm(data, instance=entry)
            if form.is_valid():
                entry = form.save(commit=False)
                entry.last_edited = timezone.now()
                entry.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Заметка обновлена',
                    'note': serialize_note(entry)
                })
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            }, status=400)

        elif action == 'delete':
            entry_id = data.get('entry_id')
            entry = get_object_or_404(MoodEntry, id=entry_id, user=request.user)
            entry.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Заметка удалена'
            })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def serialize_note(entry):
    return {
        'id': entry.id,
        'mood': entry.mood,
        'mood_display': entry.get_mood_display(),
        'notes': entry.notes,
        'date': entry.date.strftime("%d.%m.%Y %H:%M"),
        'last_edited': entry.last_edited.strftime("%d.%m.%Y %H:%M") if entry.last_edited else None,
    }


@login_required
@require_POST
def edit_note(request, pk):
    entry = get_object_or_404(MoodEntry, pk=pk, user=request.user)

    mood = request.POST.get('mood')
    notes = request.POST.get('notes')

    if not mood or not notes:
        return JsonResponse({
            'success': False,
            'error': 'Все поля обязательны для заполнения'
        })

    try:
        entry.mood = mood
        entry.notes = notes
        entry.last_edited = timezone.now()
        entry.save()

        return JsonResponse({
            'success': True,
            'mood': entry.mood,
            'notes': entry.notes,
            'last_edited': entry.last_edited.strftime("%d.%m.%Y %H:%M"),
            'mood_display': entry.get_mood_display()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["DELETE", "POST"])
def delete_note(request, pk):
    entry = get_object_or_404(MoodEntry, pk=pk, user=request.user)

    try:
        entry.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def faq_page(request):
    return render(request, 'faq/faq.html')

@login_required
def habits_page(request):
    return render(request, 'habits/add_habits.html')

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def save_habit(request):
    try:
        data = json.loads(request.body)
        user = request.user

        habit_id = data.get('habit_id')
        name = data.get('name')
        category = data.get('category')
        description = data.get('description', '')
        days_goal = int(data.get('days_goal', 30))
        reminder = data.get('reminder', False)
        color_class = data.get('color_class')
        schedule_days = data.get('schedule_days', [])

        # Создание или обновление привычки
        if habit_id:
            habit = Habit.objects.get(id=habit_id, user=user)
            habit.name = name
            habit.category = category
            habit.description = description
            habit.days_goal = days_goal
            habit.reminder = reminder
            habit.color_class = color_class
            habit.save()
        else:
            habit = Habit.objects.create(
                user=user,
                name=name,
                category=category,
                description=description,
                days_goal=days_goal,
                reminder=reminder,
                color_class=color_class
            )

        # Обновляем дни расписания
        HabitSchedule.objects.filter(habit=habit).delete()
        for day in schedule_days:
            HabitSchedule.objects.create(habit=habit, day_of_week=int(day))

        return JsonResponse({'success': True, 'habit': serialize_habit(habit)})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def serialize_habit(habit):
    return {
        'id': habit.id,
        'name': habit.name,
        'category': habit.category,
        'category_display': habit.get_category_display(),
        'description': habit.description,
        'days_goal': habit.days_goal,
        'reminder': habit.reminder,
        'color_class': habit.color_class,
        'schedule_days': list(habit.schedule.values_list('day_of_week', flat=True)),
    }

@require_GET
def get_all_habits(request):
    habits = Habit.objects.filter(user=request.user).prefetch_related('schedule')
    habits_data = []

    for habit in habits:
        habits_data.append({
            'id': habit.id,
            'name': habit.name,
            'category': habit.category,
            'category_display': habit.get_category_display(),
            'description': habit.description,
            'days_goal': habit.days_goal,
            'color_class': habit.color_class,
            'schedule_days': [s.day_of_week for s in habit.schedule.all()],
            'reminder': habit.reminder
        })

    return JsonResponse({'success': True, 'habits': habits_data})


@require_GET
def get_habits_by_day(request):
    day = request.GET.get('day')
    if not day:
        return JsonResponse({'success': False, 'error': 'Day parameter is required'})

    habits = Habit.objects.filter(
        user=request.user,
        schedule__day_of_week=day
    ).distinct().prefetch_related('schedule')

    habits_data = []

    for habit in habits:
        habits_data.append({
            'id': habit.id,
            'name': habit.name,
            'category': habit.category,
            'category_display': habit.get_category_display(),
            'description': habit.description,
            'days_goal': habit.days_goal,
            'color_class': habit.color_class,
            'schedule_days': [s.day_of_week for s in habit.schedule.all()],
            'reminder': habit.reminder
        })

    return JsonResponse({'success': True, 'habits': habits_data})

# //////////////////////////////////
@login_required
@require_POST
def add_habit(request):
    try:
        data = json.loads(request.body)
        habit = Habit.objects.create(
            user=request.user,
            name=data['name'],
            category=data['category'],
            description=data.get('description', ''),
            days_goal=data.get('days_goal', 30),
            color_class=data.get('color_class', 'bg-gray-100 text-gray-800'),
            reminder=data.get('reminder', False),
        )
        HabitSchedule.objects.bulk_create([
            HabitSchedule(habit=habit, day_of_week=day) for day in data.get('repeat_days', [])
        ])
        return JsonResponse({'status': 'success', 'habit': _habit_summary(habit)})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# @login_required
# def get_habits(request):
#     habits = Habit.objects.filter(user=request.user).prefetch_related('schedule')
#     return JsonResponse({'habits': [_habit_full(h) for h in habits]})

#////////////////////////
@login_required
def get_habits_for_day(request):
    day_of_week = int(request.GET.get('day', 0))
    habits = Habit.objects.filter(user=request.user, schedule__day_of_week=day_of_week)
    return JsonResponse({'habits': [_habit_summary(h) for h in habits]})


@login_required
@require_http_methods(["POST"])
def delete_habit(request, id):
    habit = Habit.objects.filter(id=id, user=request.user).first()
    if habit:
        habit.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Habit not found'}, status=404)



@login_required
@require_http_methods(["POST"])
def update_habit(request, id):
    try:
        data = json.loads(request.body)
        habit = get_object_or_404(Habit, id=id, user=request.user)

        for field in ['name', 'category', 'description', 'days_goal', 'color_class', 'reminder']:
            if field in data:
                setattr(habit, field, data[field])

        habit.schedule.all().delete()
        HabitSchedule.objects.bulk_create([
            HabitSchedule(habit=habit, day_of_week=day) for day in data.get('repeat_days', [])
        ])

        return JsonResponse({'status': 'success', 'habit': _habit_summary(habit)})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def get_habit(request, id):
    habit = Habit.objects.filter(id=id, user=request.user).prefetch_related('schedule').first()
    if habit:
        return JsonResponse(_habit_full(habit))
    return JsonResponse({'status': 'error', 'message': 'Habit not found'}, status=404)

@login_required
@require_POST
def track_habit(request, pk):
    try:
        # Заглушка: в будущем можно реализовать HabitCompletion
        habit = get_object_or_404(Habit, id=pk, user=request.user)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ———————————————————————
# 🔧 Вспомогательные функции
# ———————————————————————

def _habit_summary(habit):
    return {
        'id': habit.id,
        'name': habit.name,
        'category': habit.get_category_display(),
        'color_class': habit.color_class,
        'days_goal': habit.days_goal,
    }

def _habit_full(habit):
    return {
        'id': habit.id,
        'name': habit.name,
        'category': habit.category,
        'description': habit.description,
        'color_class': habit.color_class,
        'days_goal': habit.days_goal,
        'reminder': habit.reminder,
        'repeat_days': list(habit.schedule.values_list('day_of_week', flat=True)),
    }


# views.py
@require_POST
def update_schedule(request, habit_id):
    try:
        habit = Habit.objects.get(id=habit_id, user=request.user)
        data = json.loads(request.body)
        day = data.get('day')
        action = data.get('action')

        if action == 'add':
            if day not in habit.schedule_days:
                habit.schedule_days.append(day)
        elif action == 'remove':
            if day in habit.schedule_days:
                habit.schedule_days.remove(day)

        habit.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})