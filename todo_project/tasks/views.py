from django.shortcuts import render


def index(request):
    """Завдання 3 + 4: головна сторінка зі шаблоном."""
    return render(request, 'tasks/index.html')


def about(request):
    """Завдання 5: сторінка «Про ToDo»."""
    return render(request, 'tasks/about.html')
