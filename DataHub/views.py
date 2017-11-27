from django.shortcuts import render, redirect
from django.db import connection, IntegrityError, ProgrammingError
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from DataHub.models import auth_user, dataset_list, user_dataset_following, comments
from ModelClass.ModelClass import InvalidColumnNameException, UniqueConstraintException, NotNullException

# Create your views here.
def index(request):    
    popular_datasets = dataset_list.get_entries_dictionary(
        column_list=['id','creator_user_id','name', 'description', 'genre'], 
        max_rows=None, 
        row_numbers=False)
        
    for dataset in popular_datasets:
        creator_name = auth_user.get_entries_dictionary(
            column_list=['username'], max_rows=1, 
            cond_dict={ 'id': dataset['creator_user_id'] }, 
            row_numbers=False)
        if request.user.is_authenticated:
            following = user_dataset_following.check_exists(
                { 'dataset_id': dataset['id'], 
                'user_id': request.user.id })
            dataset['following'] = following
        dataset['creator_name'] = creator_name['username']
        
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
    
    created_datasets = dataset_list.get_entries_dictionary(
        column_list=['id','name', 'description', 'genre'], 
        cond_dict={'creator_user_id': request.user.id}, 
        max_rows=None, row_numbers=False)
    
    following_datasets = user_dataset_following.get_entries_dictionary(
    column_list=['dataset_id'], cond_dict={'user_id':request.user.id}, 
    max_rows=None, row_numbers=False)
    
    for dataset in following_datasets:
        dataset_info = dataset_list.get_entries_dictionary(
        column_list=['name','description','creator_user_id','genre'],
        cond_dict={'id':dataset['dataset_id']}, 
        max_rows=1,
        row_numbers=False)
        creator_name = auth_user.get_entries_dictionary(
        column_list=['username'],
        cond_dict={'id':dataset_info['creator_user_id']},
        max_rows=1,
        row_numbers=False)
        dataset['creator_name'] = creator_name['username']
        dataset.update(dataset_info)
        
    user_comments = comments.get_entries_dictionary(
    column_list=['id','dataset_id','content'],
    cond_dict={'user_id':request.user.id},
    max_rows=None, row_numbers=False)
    
    for comment in user_comments:
        dataset = dataset_list.get_entries_dictionary(
        column_list=['name'],
        cond_dict={'id': comment['dataset_id']},
        max_rows=1,
        row_numbers=False)
        comment['dataset_name'] = dataset['name']
    
    context = {
        'auth': True,
        'user': request.user,
        'user_info': request.user,
        'created_datasets': created_datasets, 
        'following_datasets': following_datasets,
        'comments': user_comments,
    }
    return render(request, 'profile.html', context)

def dataset(request, dataset):
    context = {}
    
    dataset_info = dataset_list.get_entries_dictionary(
    column_list=['id','name', 'creator_user_id', 'endorsed_by', 'description', 'genre'], 
    cond_dict={'id': dataset }, max_rows=1, row_numbers=False)

    user_info = auth_user.get_entries_dictionary(
        column_list=['username'], 
        max_rows=1,
        cond_dict={ 'id': dataset_info['creator_user_id'] }, 
        row_numbers=False)
    dataset_info['username'] = user_info['username']
    
    dataset_comments = comments.get_entries_dictionary(
        column_list=['user_id','content'],
        max_rows=None,
        cond_dict={ 'dataset_id':dataset },
        row_numbers=False)
    context['comments'] = dataset_comments
    
    if not request.user.is_authenticated or not dataset:
        context['auth'] = False
    else:
        context['auth'] = True
        context['user'] = request.user
        following = user_dataset_following.check_exists(
            { 'dataset_id': dataset_info['id'],
            'user_id': request.user.id })
        dataset_info['following'] = following
        
    context['dataset_info'] = dataset_info
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
    elif origin == 'dataset':
        return redirect('/dataset/' + id)
    
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
    elif origin == 'dataset':
        return redirect('/dataset/' + id)
    elif origin == 'profile':
        return redirect('/profile/')
    
def comment(request, dataset):
    content = request.POST['content'].strip()
    comments.insert_new_entry({
        'user_id': request.user.id, 
        'content': content,
        'dataset_id': dataset
    })
    return redirect('/dataset/' + dataset)
    
def user(request, username):
    if request.user.username == username:
        return redirect('/profile/')
    
    user_info = auth_user.get_entries_dictionary(
        column_list=['id','email','first_name','last_name'], 
        max_rows=1,
        cond_dict={ 'username': username }, 
        row_numbers=False
    )
    user_info['username'] = username
    
    created_datasets = dataset_list.get_entries_dictionary(
        column_list=['id','name', 'description', 'genre'], 
        cond_dict={'creator_user_id': user_info['id'] }, 
        max_rows=None, row_numbers=False)
    
    following_datasets = user_dataset_following.get_entries_dictionary(
    column_list=['dataset_id'], cond_dict={'user_id':user_info['id']}, 
    max_rows=None, row_numbers=False)
    
    for dataset in following_datasets:
        dataset_info = dataset_list.get_entries_dictionary(
        column_list=['name','description','creator_user_id','genre'],
        cond_dict={'id':dataset['dataset_id']}, 
        max_rows=1,
        row_numbers=False)
        creator_name = auth_user.get_entries_dictionary(
        column_list=['username'],
        cond_dict={'id':dataset_info['creator_user_id']},
        max_rows=1,
        row_numbers=False)
        dataset['creator_name'] = creator_name['username']
        dataset.update(dataset_info)
    
    context = {
        'auth': False,
        'user_info': user_info,
        'created_datasets': created_datasets, 
        'following_datasets': following_datasets,
    }
    
    if request.user.is_authenticated:
        context['auth'] = True
    return render(request, 'profile.html', context)

def delete_dataset(request, dataset):
    creator_user_id = dataset_list.get_entries_dictionary(
    column_list=['creator_user_id'],
    cond_dict={'id':dataset}, 
    max_rows=1,
    row_numbers=False)

    if not (creator_user_id['creator_user_id'] == request.user.id):
        messages.info(request, 'You cannot delete that dataset')
        return redirect('/')
    user_dataset_following.delete_entries({'dataset_id':dataset})
    dataset_list.delete_entries({'id':dataset})

    messages.success(request, 'Dataset deleted')
    return redirect('/profile/')

def popular_datasets(request):
    popular_datasets = dataset_list.get_entries_dictionary(
        column_list=['id','creator_user_id','name', 'description', 'genre'], 
        max_rows=None, 
        row_numbers=False)
        
    for dataset in popular_datasets:
        creator_name = auth_user.get_entries_dictionary(
            column_list=['username'], max_rows=1, 
            cond_dict={ 'id': dataset['creator_user_id'] }, 
            row_numbers=False)
        # if request.user.is_authenticated:
        #     following = user_dataset_following.check_exists(
        #         { 'dataset_id': dataset['id'], 
        #         'user_id': request.user.id })
        #     dataset['following'] = following
        dataset['creator_name'] = creator_name['username']
        
    context = { 
        'auth': False, 
        'popular_datasets': reversed(popular_datasets)
     }
     
    if request.user.is_authenticated:
        context['auth'] = True
        context['user'] = request.user
    return render(request, 'popular_datasets.html', context)

def popular_users(request):
    popular_datasets = dataset_list.get_entries_dictionary(
        column_list=['id','creator_user_id','name', 'description', 'genre'], 
        max_rows=None, 
        row_numbers=False)
        
    for dataset in popular_datasets:
        creator_name = auth_user.get_entries_dictionary(
            column_list=['username'], max_rows=1, 
            cond_dict={ 'id': dataset['creator_user_id'] }, 
            row_numbers=False)
        # if request.user.is_authenticated:
        #     following = user_dataset_following.check_exists(
        #         { 'dataset_id': dataset['id'], 
        #         'user_id': request.user.id })
        #     dataset['following'] = following
        dataset['creator_name'] = creator_name['username']
        
    context = { 
        'auth': False, 
        'popular_datasets': reversed(popular_datasets)
     }
     
    if request.user.is_authenticated:
        context['auth'] = True
        context['user'] = request.user
    return render(request, 'popular_users.html') #removed context returned

def popular_genres(request):
    popular_datasets = dataset_list.get_entries_dictionary(
        column_list=['id','creator_user_id','name', 'description', 'genre'], 
        max_rows=None, 
        row_numbers=False)
        
    for dataset in popular_datasets:
        creator_name = auth_user.get_entries_dictionary(
            column_list=['username'], max_rows=1, 
            cond_dict={ 'id': dataset['creator_user_id'] }, 
            row_numbers=False)
        # if request.user.is_authenticated:
        #     following = user_dataset_following.check_exists(
        #         { 'dataset_id': dataset['id'], 
        #         'user_id': request.user.id })
        #     dataset['following'] = following
        dataset['creator_name'] = creator_name['username']
        
    context = { 
        'auth': False, 
        'popular_datasets': reversed(popular_datasets)
     }
     
    if request.user.is_authenticated:
        context['auth'] = True
        context['user'] = request.user
    return render(request, 'popular_genres.html') #removed context returned

def statistics(request):
    popular_datasets = dataset_list.get_entries_dictionary(
        column_list=['id','creator_user_id','name', 'description', 'genre'], 
        max_rows=None, 
        row_numbers=False)
        
    for dataset in popular_datasets:
        creator_name = auth_user.get_entries_dictionary(
            column_list=['username'], max_rows=1, 
            cond_dict={ 'id': dataset['creator_user_id'] }, 
            row_numbers=False)
        # if request.user.is_authenticated:
        #     following = user_dataset_following.check_exists(
        #         { 'dataset_id': dataset['id'], 
        #         'user_id': request.user.id })
        #     dataset['following'] = following
        dataset['creator_name'] = creator_name['username']
        
    context = { 
        'auth': False, 
        'popular_datasets': reversed(popular_datasets)
     }
     
    if request.user.is_authenticated:
        context['auth'] = True
        context['user'] = request.user
    return render(request, 'statistics.html') #removed context returned