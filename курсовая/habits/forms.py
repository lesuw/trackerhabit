from django import forms
from .models import MoodEntry, Habit, HabitSchedule

class HabitForm(forms.ModelForm):
    repeat_days = forms.MultipleChoiceField(
        choices=HabitSchedule.DAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Повторять в дни недели"
    )

    class Meta:
        model = Habit
        fields = ['name', 'category', 'description', 'days_goal', 'reminder', 'color_class']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_days_goal(self):
        days_goal = self.cleaned_data.get('days_goal')
        if days_goal < 1:
            raise forms.ValidationError("Цель по дням должна быть больше нуля.")
        return days_goal

    def save(self, commit=True):
        habit = super().save(commit=commit)

        # Сохраняем расписание, если repeat_days есть в cleaned_data
        if self.cleaned_data.get('repeat_days'):
            # Удалим старые, чтобы не дублировались
            HabitSchedule.objects.filter(habit=habit).delete()
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