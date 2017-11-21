from django.shortcuts import render, redirect
from django.db import connection, IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def index(request):
    context = {}
    if request.user.is_authenticated:
        context = { 'user': request.user.id }
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
        context = {}
        return render(request, 'sign_up.html', context)
    elif request.method == 'POST':
        params = request.POST
        try:
            user = User.objects.create_user(params['username'], params['email'], params['password'])
        except IntegrityError:
            context['duplicate_username'] = True
            return render(request, 'sign_up.html', context)
        return redirect('/')

def sign_in(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'sign_in.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            context = { 'error': 'Invalid login credentials' }
            return render(request, 'sign_in.html', context)
