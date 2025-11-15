from django.shortcuts import render


def home(request):
    return render(request, 'DNA_website/index.html')

