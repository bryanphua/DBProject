from django.shortcuts import render, redirect
from django.db import connection, IntegrityError, ProgrammingError
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from DataHub.models import auth_user, dataset_list, user_dataset_following
from ModelClass.ModelClass import InvalidColumnNameException, UniqueConstraintException, NotNullException

# Create your views here.
def index(request):    
    popular_datasets_get = dataset_list.get_entries(
        column_list=['id','creator_user_id','name', 'description', 'genre'], 
        max_rows=None, 
        row_numbers=False)[1]
        
    popular_datasets = []
    for dataset in popular_datasets_get:
        creator_name = auth_user.get_entries(column_list=['username'], max_rows=1, cond_dict={ 'id': dataset[1] }, row_numbers=False)[1][0][0]
        following = user_dataset_following.get_entries(column_list=None, max_rows=1, cond_dict={ 'dataset_id': dataset[0], 'user_id': request.user.id }, row_numbers=True)
        
        dataset = list(dataset)
        dataset.append(creator_name)
        dataset.append(following)
        
        popular_datasets.append(dataset)
    context = { 
        'auth': False, 
        'popular_datasets': reversed(popular_datasets)
     }
    if request.user.is_authenticated:
        context['auth'] = True
        context['user'] = request.user
    return render(request, 'index.html', context)

def profile(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please login to view your profile')
        return redirect('/')
    
    created_datasets = dataset_list.get_entries(column_list=['id','name', 'description', 'genre'], cond_dict={'creator_user_id': request.user.id}, max_rows=None, row_numbers=False)[1]

    context = {
        'auth': True,
        'user': request.user,
        'created_datasets': created_datasets
    }
    return render(request, 'profile.html', context)

def dataset(request, dataset):
    dataset_info = dataset_list.get_entries(column_list=['id','name', 'creator_user_id', 'endorsed_by', 'description', 'genre'], cond_dict={'id': dataset }, max_rows=1, row_numbers=False)[1][0]
    dataset_info += auth_user.get_entries(column_list=['username'], max_rows=1, cond_dict={ 'id': dataset_info[2] }, row_numbers=False)[1][0]
    context = { 'dataset_info': dataset_info }
    if not request.user.is_authenticated or not dataset:
        context['auth'] = False
    else:
        context['auth'] = True
        context['user'] = request.user
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
        try:
            dataset_list.insert_new_entry({
                'name':params['title'],
                'creator_user_id':request.user.id,
                'endorsed_by':'placeholder',
                'description':params['description'],
                'genre':params['genre']
            })
            messages.success(request, 'Dataset created successfully')
        except ProgrammingError:
            messages.info(request, 'Invalid characters used')
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

def follow(request, id, origin):
    try:
        user_dataset_following.insert_new_entry({
            'user_id': request.user.id,
            'dataset_id': id
        })
        messages.success(request, "You are now following the dataset")
    except IntegrityError:
        messages.info(request, "You are already following this dataset!")
    
    if origin == 'index':
        return redirect('/')
    else:
        return redirect('/')
    
def unfollow(request, id, origin):
    try:
        user_dataset_following.delete_entries({
            'user_id': request.user.id,
            'dataset_id': id
        })
        messages.success(request, "You have unfollowed the dataset")
    except IntegrityError:
        messages.info(request, "You have not followed this dataset!")
    
    if origin == 'index':
        return redirect('/')
    else:
        return redirect('/')
    