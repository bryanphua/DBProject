from django.shortcuts import render, redirect
from django.db import connection, IntegrityError
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from DataHub.models import auth_user
from .forms import sign_in_form, sign_up_form

# Create your views here.
def index(request):
    context = { 'auth': False }
    print ('test', auth_user.get_entries(column_list=['email']))
    if request.user.is_authenticated:
        context = {
            'auth': True,
            'user': request.user
        }
    return render(request, 'index.html', context)

def profile(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please login to view your profile')
        return redirect('/')
    context = {
        'auth': True,
        'user': request.user
    }
    return render(request, 'profile.html', context)

def dataset(request):
    if not request.user.is_authenticated:
        context = {}
    else:
        context = {
            'auth': True,
            'user': request.user
        }
    return render(request, 'dataset.html', context)

def new_dataset(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please login to create a dataset')
        return redirect('/')
    context = {
        'auth': True,
        'user': request.user
    }
    return render(request, 'create_dataset.html', context)

def sign_up(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'GET':
        context = {}
        return render(request, 'sign_up.html', context)
    elif request.method == 'POST':
        params = request.POST
        form = sign_up_form(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(params['username'], params['email'], params['password'])
                return redirect('/')
            except IntegrityError:
                context = { 'duplicate_username': True }
                return render(request, 'sign_up.html', context)
        else:
            context = { 'form': form }
            return render(request, 'sign_up.html', context)

def sign_in(request):
    if request.user.is_authenticated:
        return redirect('/')
    context = {}
    if request.method == 'GET':
        return render(request, 'sign_in.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login success')
            return redirect('/')
        else:
            messages.error(request, 'Invalid login credentials')
            return render(request, 'sign_in.html', context)

def sign_out(request):
    logout(request)
    messages.success(request, 'You have signed out successfully')
    return redirect('/')
