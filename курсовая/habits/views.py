from django.shortcuts import render

def add_habits(request):
    return render(request, 'habits/add_habits.html')
# Create your views here.
