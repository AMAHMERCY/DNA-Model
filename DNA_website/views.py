from django.shortcuts import render


def home(request):
    return render(request, 'DNA_website/index.html')
def login_view(request):
    return render(request, 'DNA_website/login.html')
def register_view(request):
    return render(request, 'DNA_website/register.html')