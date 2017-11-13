from django.shortcuts import render

# Create your views here.
def index(request):
    context = {}
    return render(request, 'index.pug', context)

def profile(request):
    context = {}
    return render(request, 'profile.html', context)

def dataset(request):
    context = {}
    return render(request, 'dataset.html', context)

def new_dataset(request):
    context = {}
    return render(request, 'create_dataset.html', context)
