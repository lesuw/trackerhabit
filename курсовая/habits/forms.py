from .models import MoodEntry, Habit, HabitSchedule
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone


class HabitForm(forms.ModelForm):
    repeat_days = forms.MultipleChoiceField(
        choices=HabitSchedule.DAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Повторять в дни недели"
    )

    # Поле для времени напоминания (будет сохраняться как время в Habit)
    reminder_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=False,
        label="Время напоминания"
    )

    class Meta:
        model = Habit
        fields = ['name', 'category', 'description', 'days_goal', 'reminder', 'color_class']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Опишите свою привычку...'}),
            'name': forms.TextInput(attrs={'placeholder': 'Например: Утренняя зарядка'}),
        }
        labels = {
            'days_goal': 'Цель (количество дней)',
            'reminder': 'Напоминание',
        }
        help_texts = {
            'days_goal': 'Сколько дней подряд вы хотите выполнять эту привычку?',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Если редактируем существующую привычку, заполняем repeat_days
        if self.instance.pk:
            self.fields['repeat_days'].initial = list(
                self.instance.schedule.values_list('day_of_week', flat=True)
            )

    def clean_days_goal(self):
        days_goal = self.cleaned_data.get('days_goal')
        if days_goal < 1:
            raise forms.ValidationError("Цель по дням должна быть больше нуля.")
        if days_goal > 365:
            raise forms.ValidationError("Установите цель менее 366 дней.")
        return days_goal

    def clean(self):
        cleaned_data = super().clean()
        reminder = cleaned_data.get('reminder')
        reminder_time = cleaned_data.get('reminder_time')

        # Проверка, что если reminder=True, то указано время
        if reminder and not reminder_time:
            self.add_error('reminder_time', "Укажите время для напоминания")

        return cleaned_data

    def save(self, commit=True):
        habit = super().save(commit=commit)

        # Сохраняем расписание дней
        if commit:
            HabitSchedule.objects.filter(habit=habit).delete()
            if self.cleaned_data.get('repeat_days'):
                for day in self.cleaned_data['repeat_days']:
                    HabitSchedule.objects.create(habit=habit, day_of_week=day)

        return habit


class MoodEntryForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ['mood', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Опишите, что повлияло на ваше настроение сегодня...',
                'class': 'form-textarea'
            }),
        }
        labels = {
            'mood': 'Настроение',
            'notes': 'Заметка'
        }