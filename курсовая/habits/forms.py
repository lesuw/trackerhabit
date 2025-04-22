from django import forms
from .models import Habit


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'category', 'description', 'days_goal', 'reminder', 'color_class', 'repeat_days']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'repeat_days': forms.CheckboxSelectMultiple(),
        }

    # Дополнительная валидация для категории (по желанию)
    def clean_days_goal(self):
        days_goal = self.cleaned_data.get('days_goal')
        if days_goal < 1:
            raise forms.ValidationError("Цель по дням должна быть больше нуля.")
        return days_goal
