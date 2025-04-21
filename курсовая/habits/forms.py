# forms.py
from django import forms
from .models import MoodEntry

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