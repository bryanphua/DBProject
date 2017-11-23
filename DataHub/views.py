from django.shortcuts import render, redirect
from django.db import connection, IntegrityError
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from DataHub.models import auth_user, dataset_list
from ModelClass.ModelClass import InvalidColumnNameException, UniqueConstraintException, NotNullException

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
    context = {
        'auth': True,
        'user': request.user
    }
    if not request.user.is_authenticated:
        messages.info(request, 'Please login to create a dataset')
        return redirect('/')
    if request.method == 'POST':
        params = request.POST
        if (not params['title']) or (not params['genre']):
            messages.info(request, 'Did you forget to fill in any fields?')
            # context['name'] = params['title']
            return render(request, 'create_dataset.html', context)

        dataset_list.insert_new_entry({
            'name':params['title'],
            'creator_user_id':request.user.id,
            'endorsed_by':'placeholder',
            'description':params['description'],
            'genre':params['genre']
        })
        messages.success(request, 'Dataset created successfully')
    return render(request, 'create_dataset.html', context)


def sign_up(request):
    context = {}
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'GET':
        return render(request, 'sign_up.html', context)
    elif request.method == 'POST':
        params = request.POST
        if (not params['username']) or (not params['email']) or (not params['password']) or (not params['first_name']):
            messages.info(request, 'Required fields cannot be blank!')
            return render(request, 'sign_up.html', context)
        try:
            user = User.objects.create_user(
                username=params['username'],
                email=params['email'],
                password=params['password']
            )
            user.first_name = params['first_name']
            user.last_name = params['last_name']
            user.save()
        except IntegrityError:
            messages.info(request, 'Username already taken :(')
            return render(request, 'sign_up.html', context)
        login(request, user)
        messages.success(request, 'Account successfully created')
        return redirect('/')

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
            messages.info(request, 'Invalid login credentials')
            return render(request, 'sign_in.html', context)

def sign_out(request):
    logout(request)
    messages.success(request, 'You have signed out successfully')
    return redirect('/')
