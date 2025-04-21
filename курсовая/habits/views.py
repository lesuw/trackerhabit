from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from .models import MoodEntry
from .forms import MoodEntryForm


@login_required
def notes(request):
    # Обработка фильтров
    mood_filter = request.GET.get('mood')
    date_filter = request.GET.get('date')

    # Получение записей с фильтрами
    entries = MoodEntry.objects.filter(user=request.user)

    if mood_filter:
        entries = entries.filter(mood=mood_filter)
    if date_filter:
        entries = entries.filter(date__date=date_filter)

    entries = entries.order_by('-date')

    # Пагинация
    paginator = Paginator(entries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Обработка формы
    if request.method == 'POST':
        form = MoodEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, 'Запись успешно добавлена')
            return redirect('notes')
    else:
        form = MoodEntryForm()

    context = {
        'page_obj': page_obj,
        'form': form,
        'mood_filter': mood_filter,
        'date_filter': date_filter,
    }
    return render(request, 'notes/notes.html', context)


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

def add_habits(request):
    return render(request, 'habits/add_habits.html')