from django.shortcuts import render, redirect
from django.db import connection, IntegrityError, ProgrammingError
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from DataHub.models import auth_user, dataset_list, user_dataset_following, comments, dataset_rating, comments_vote
from ModelClass.ModelClass import InvalidColumnNameException, UniqueConstraintException, NotNullException

def search_dataset(request, keyword, columns, sort):
    # Takes in attributes we're interested in as a list 
    if len(columns) == 0:
        columns = ['name', 'username', 'genre']
        
    # Formulating our WHERE condition
    condition = ""
    for i in range(len(columns)):
        if i == 0:
            condition += str(columns[i]) + " LIKE %s"
        else:
            condition += " OR " + str(columns[i]) + " LIKE %s"
            
    # Also takes in sorting method as a string
    if sort != None and sort !='null':
        sort = sort.split('-')
        condition += " ORDER BY " + str(sort[0]) + " " + str(sort[1])
    
    following = ""
    if request.user.is_authenticated:
        # check if sessions user is following the dataset
        # isFollowing is a function created in our schema
        following = ", isFollowing(" + str(request.user.id) + ", L.id) AS following"
    
    with connection.cursor() as cursor:
        statement = "SELECT L.id, name, description, username, genre, rating"+ following +" FROM dataset_list L JOIN auth_user U ON L.creator_user_id=U.id WHERE " + condition
        cursor.execute(statement, [keyword]*len(columns))
        keys = [d[0] for d in cursor.description]
        values = [dict(zip(keys, row)) for row in cursor.fetchall()]
    
    return values

# Search function
def search(request):
    keyword = request.GET.get('q')
    if not keyword:
        return redirect("/")
    context = { 'auth': False, 'keyword':keyword }
    
    filters = []
    if request.GET.get('name') == 'true':
        filters.append('name')
        context['filter_name'] = True
    if request.GET.get('username') == 'true':
        filters.append('username')
        context['filter_username'] = True
    if request.GET.get('genre') == 'true':
        filters.append('genre')
        context['filter_genre'] = True
    sort = request.GET.get('sort')
    context['sort'] = sort
    
    if request.user.is_authenticated:
        context['auth'] = True
    keyword = '%' + keyword + '%'
    
    # Getting relevant datasets (general)
    context['datasets'] = search_dataset(request, keyword, filters, sort)
    
    # Getting relevant users
    with connection.cursor() as cursor:
        statement = "SELECT username FROM auth_user WHERE username LIKE %s"
        cursor.execute(statement, [keyword])
        keys = [d[0] for d in cursor.description]
        values = [dict(zip(keys, row)) for row in cursor.fetchall()]
    context['users'] = values

    return render(request, 'search_results.html', context)

# Populating data for our index page
def index(request):
    context = { 'auth': False }
    
    following = ""
    if request.user.is_authenticated:
        context['auth'] = True
        context['user'] = request.user
        # check if sessions user is following the dataset
        # isFollowing is a function created in our schema
        following = ", isFollowing(" + str(request.user.id) + ", L.id) AS following"
    
    # Retrieving information of top 10 newest datasets
    with connection.cursor() as cursor:
        statement = "SELECT L.id, name, description, username, genre, rating" + following + " FROM dataset_list L JOIN auth_user U ON L.creator_user_id=U.id ORDER BY datetime_created DESC LIMIT 10"
        cursor.execute(statement)
        keys = [d[0] for d in cursor.description]
        values = [dict(zip(keys, row)) for row in cursor.fetchall()]
    new_datasets = values
    
    context['popular_datasets'] = new_datasets
     
    return render(request, 'index.html', context)

def profile(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please login to view your profile')
        return redirect('/')
    
    # Retrieving information of created datasets
    created_datasets = dataset_list.get_entries_dictionary(
        column_list=['id','name', 'description', 'genre'], 
        cond_dict={'creator_user_id': request.user.id}, 
        max_rows=None, row_numbers=False)
        
    # Retrieving information of followed datasets
    with connection.cursor() as cursor:
        statement = "SELECT dataset_id, name, description, username, genre FROM user_dataset_following F JOIN dataset_list L ON F.dataset_id = L.id JOIN auth_user U ON L.creator_user_id=U.id WHERE F.user_id =" + str(request.user.id)
        cursor.execute(statement)
        keys = [d[0] for d in cursor.description]
        values = [dict(zip(keys, row)) for row in cursor.fetchall()]
    following_datasets = values
    print(following_datasets)
    
    # Retrieving information of comments (CV is a view we created)
    with connection.cursor() as cursor:
        statement = "SELECT C.id as id, dataset_id, content, user_id, COALESCE(CV.votes, 0) as votes, name FROM comments C JOIN dataset_list L ON C.dataset_id = L.id LEFT JOIN CV ON C.id = CV.comment_id WHERE C.user_id = " + str(request.user.id)
        cursor.execute(statement)
        keys = [d[0] for d in cursor.description]
        values = [dict(zip(keys, row)) for row in cursor.fetchall()]
    user_comments = values
    
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
    
    # Retrieving information regarding dataset
    dataset_info = dataset_list.get_entries_dictionary(
    column_list=['id','name', 'creator_user_id', 'endorsed_by', 'description', 'genre', 'rating', 'datetime_created', 'follower_count'], 
    cond_dict={'id': dataset }, max_rows=1)
    
    # Getting username of dataset creator
    user_info = auth_user.get_entries_dictionary(
        column_list=['username'],max_rows=1,
        cond_dict={ 'id': dataset_info['creator_user_id'] })
    dataset_info['username'] = user_info['username']
    
    # Retrieving comments in dataset (CV is a view we created)
    with connection.cursor() as cursor:
        statement = "SELECT C.id as id, user_id, username, dataset_id, content, COALESCE(CV.votes, 0) AS votes FROM comments C JOIN auth_user U ON C.user_id = U.id LEFT JOIN CV ON C.id = CV.comment_id WHERE dataset_id = " + str(dataset)
        cursor.execute(statement)
        keys = [d[0] for d in cursor.description]
        values = [dict(zip(keys, row)) for row in cursor.fetchall()]
    context['comments'] = values
    
    recommended = dataset_list.get_entries_dictionary(
        column_list=['id','name','genre'],
        cond_dict={'genre':dataset_info['genre']})
    context['recommended'] = recommended
    
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
            return render(request, 'create_dataset.html', context)
        try:
            dataset_list.insert_new_entry({
                'name':params['title'],
                'creator_user_id':request.user.id,
                'endorsed_by':params['endorsed_by'],
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
                password=params['password'])
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
    if not request.user.is_authenticated:
        messages.info(request, 'Please login to comment!')
        return redirect('/dataset/' + dataset)
    content = request.POST['content'].strip()
    if len(content) == 0:
        messages.info(request, 'Comment field cannot be blank!')
        return redirect('/dataset/' + dataset)
    try:
        comments.insert_new_entry({
            'user_id': request.user.id, 
            'content': content,
            'dataset_id': dataset
        })
    except ProgrammingError:
        messages.info(request, 'Invalid characters used.')
    return redirect('/dataset/' + dataset)
    
def user(request, username):
    if request.user.username == username:
        return redirect('/profile/')
    
    user_info = auth_user.get_entries_dictionary(
        column_list=['id','email','first_name','last_name'], 
        max_rows=1,
        cond_dict={ 'username': username })
    user_info['username'] = username
    
    created_datasets = dataset_list.get_entries_dictionary(
        column_list=['id','name', 'description', 'genre'], 
        cond_dict={'creator_user_id': user_info['id'] }, max_rows=None)
    
    # Retrieving information of followed datasets
    with connection.cursor() as cursor:
        statement = "SELECT dataset_id, name, description, username, genre FROM user_dataset_following F JOIN dataset_list L ON F.dataset_id = L.id JOIN auth_user U ON L.creator_user_id=U.id WHERE F.user_id =" + str(user_info['id'])
        cursor.execute(statement)
        keys = [d[0] for d in cursor.description]
        values = [dict(zip(keys, row)) for row in cursor.fetchall()]
    following_datasets = values
    
    # Retrieving comments in dataset (CV is a view we created)
    with connection.cursor() as cursor:
        statement = "SELECT C.id as id, user_id, dataset_id, content, coalesce(CV.votes, 0) AS votes, name FROM comments C JOIN dataset_list L ON C.dataset_id = L.id LEFT JOIN CV ON C.id = CV.comment_id WHERE C.user_id = " + str(user_info['id'])
        cursor.execute(statement)
        keys = [d[0] for d in cursor.description]
        values = [dict(zip(keys, row)) for row in cursor.fetchall()]
    user_comments = values
    
    context = {
        'auth': False,
        'user_info': user_info,
        'created_datasets': created_datasets, 
        'following_datasets': following_datasets,
        'comments': user_comments,
    }
    
    if request.user.is_authenticated:
        context['auth'] = True
    return render(request, 'profile.html', context)

def delete_dataset(request, dataset):
    dataset_list.delete_entries({'id':dataset})
    messages.success(request, 'Dataset deleted')
    return redirect('/profile/')

def delete_comment(request, comment):
    comments.delete_entries({'id':comment})
    messages.success(request, 'Comment deleted')
    return redirect('/profile/')

def rate_dataset(request, dataset):
    rating = request.POST['rating']
    if not request.user.is_authenticated:
        messages.info(request, "Please login to rate!")
        return redirect('/dataset/' + dataset)
    try:
        dataset_rating.insert_new_entry({
            'user_id':request.user.id,
            'dataset_id':dataset,
            'rating':rating
        })
    except IntegrityError:
        dataset_rating.update_entries({
            'user_id':request.user.id,
            'dataset_id':dataset,
            'rating':rating
        }, {
            'user_id':request.user.id,
            'dataset_id':dataset
        })
    messages.success(request, "You have rated!")
    return redirect('/dataset/' + dataset)

def rate_comment(request, comment, rate, origin):
    try:
        comments_vote.insert_new_entry({
            'user_id': request.user.id,
            'comment_id': comment,
            'vote': rate
        })
    except IntegrityError:
        comments_vote.update_entries({
            'user_id': request.user.id,
            'comment_id': comment,
            'vote': rate
        }, {
            'user_id': request.user.id,
            'comment_id': comment
        })
    messages.success(request, "You have voted!")
    return redirect('/dataset/' + origin)

def popular_datasets(request):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        messages.info(request, "You do not have access to the page!")
        return redirect("/")
    
    context = {}
    sort = request.GET.get('sort')
    context['sort'] = sort
    
    # Default sorting 
    condition = " ORDER BY ((follower_count+1)*(rating+1)) DESC"
    if sort != None and sort !='null':
        sort = sort.split('-')
        condition = "ORDER BY " + str(sort[0]) + " " + str(sort[1])
    
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM dataset_list " + condition + " LIMIT 10")
        popular_datasets = dictfetchall(cursor)

    for dataset in popular_datasets:
        creator_name = auth_user.get_entries_dictionary(
            column_list=['username'], max_rows=1,
            cond_dict={ 'id': dataset['creator_user_id'] })
        dataset['creator_name'] = creator_name['username']

    context['popular_datasets'] = popular_datasets
    context['auth'] = True
    context['user'] = request.user

    return render(request, 'popular_datasets.html', context)

def popular_users(request):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        messages.info(request, "You do not have access to the page!")
        return redirect("/")
    
    context = {}
    sort = request.GET.get('sort')
    context['sort'] = sort
    
    # Default sorting 
    condition = " CAST(SUM((follower_count+1)*(rating+1)) AS SIGNED) default_order,"
    criteria = "default_order"
    if sort != None and sort !='null':
        condition = ""
        sort = sort.split('-')
        if str(sort[0]) == 'rating':
            criteria = "avg_ratings"
        elif str(sort[0]) == 'follower_count':
            criteria = "total_followers"
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT creator_user_id,"+ condition +" CAST(SUM(follower_count) AS SIGNED) total_followers, CAST(AVG(rating) AS SIGNED) avg_ratings, COUNT(creator_user_id) num_of_datasets FROM dataset_list GROUP BY creator_user_id ORDER BY "+ criteria +" DESC")
        popular_users = dictfetchall(cursor)

    for user in popular_users:
        username = auth_user.get_entries_dictionary(
            column_list=['username'], max_rows=1,
            cond_dict={ 'id': user['creator_user_id'] })
        user['username'] = username['username']
        
    context['popular_users'] = popular_users
    context['auth'] = True
    context['user'] = request.user
     
    return render(request, 'popular_users.html', context)

def popular_genres(request):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        messages.info(request, "You do not have access to the page!")
        return redirect("/")
    
    context = {}
    sort = request.GET.get('sort')
    context['sort'] = sort
    
    # Default sorting 
    condition = 'num_of_datasets'
    if sort != None and sort !='null':
        sort = sort.split('-')
        if str(sort[0]) == 'rating':
            condition = 'avg_rating'
        elif str(sort[0]) == 'follower_count':
            condition = 'followers'
            
    with connection.cursor() as cursor:
        cursor.execute("SELECT genre, COUNT(genre) num_of_datasets, AVG(rating) avg_rating, SUM(follower_count) followers FROM dataset_list GROUP BY genre ORDER BY "+ condition +" DESC")
        popular_genres = dictfetchall(cursor)

    context['popular_genres'] = popular_genres
    context['auth'] = True
    context['user'] = request.user

    return render(request, 'popular_genres.html', context)

def statistics(request):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        messages.info(request, "You do not have access to the page!")
        return redirect("/")
    
    popular_datasets = dataset_list.get_entries_dictionary(
        column_list=['id','creator_user_id','name', 'description', 'genre'],max_rows=None)
        
    for dataset in popular_datasets:
        creator_name = auth_user.get_entries_dictionary(
            column_list=['username'], max_rows=1,
            cond_dict={ 'id': dataset['creator_user_id'] })
        dataset['creator_name'] = creator_name['username']
        
    context = { 
        'popular_datasets': reversed(popular_datasets),
        'auth': True, 
        'user': request.user
     }

    return render(request, 'statistics.html', context)

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def staff_sign_up(request):
    if request.user.is_authenticated:
        messages.info(request, "Please sign out before trying to sign up!")
        return redirect('/')
    elif request.method == 'GET':
        return render(request, 'staff_sign_up.html')
    elif request.method == 'POST':
        params = request.POST
        if (not params['username']) or (not params['email']) or (not params['password']) or (not params['first_name']):
            messages.info(request, 'Required fields cannot be blank!')
            return redirect('/staffme/')
        
        if params['code'] == "purplepandas":
            try:
                user = User.objects.create_user(
                    username=params['username'],
                    email=params['email'],
                    password=params['password'])
                user.first_name = params['first_name']
                user.last_name = params['last_name']
                user.is_staff = True
                user.save()
            except IntegrityError:
                messages.info(request, 'Username already taken :(')
                return redirect('/staffme/')
            login(request, user)
            messages.success(request, 'Staff account successfully created!')
            return redirect('/')
        else:
            messages.info(request, "Wrong code :(")
            return redirect('/staffme/')
