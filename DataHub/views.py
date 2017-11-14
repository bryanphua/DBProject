from django.shortcuts import render
from django.db import connection, IntegrityError
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    context = {}
    return render(request, 'index.html', context)

def profile(request):
    context = {}
    return render(request, 'profile.html', context)

def dataset(request):
    context = {}
    return render(request, 'dataset.html', context)

def new_dataset(request):
    context = {}
    return render(request, 'create_dataset.html', context)

def sign_up(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'sign_up.html', context)
    elif request.method == 'POST':
        params = request.POST
        try:
            user = User.objects.create_user(params['username'], params['password'])
        except IntegrityError:
            context['duplicate_username'] = True
        return render(request, 'sign_up.html', context)
