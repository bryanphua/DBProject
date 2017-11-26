"""DBProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^profile/$', views.profile, name = 'profile'),
    url(r'^dataset/$', RedirectView.as_view(url='/', permanent=False), name = 'r_dataset'),
    url(r'^dataset/(?P<dataset>[0-9]{1,11})/$', views.dataset, name = 'dataset'),
    url(r'^new/$', views.new_dataset, name = 'new'),
    url(r'^signup/$', views.sign_up, name = 'sign_up'),
    url(r'^signin/$', views.sign_in, name = 'sign_in'),
    url(r'^signout/$', views.sign_out, name = 'sign_out'),
    url(r'^follow/(?P<id>[0-9]{1,11})/(?P<origin>.*)/$', views.follow, name = 'follow'),
    url(r'^unfollow/(?P<id>[0-9]{1,11})/(?P<origin>.*)/$', views.unfollow, name = 'unfollow'),
    url(r'^comment/(?P<dataset>[0-9]{1,11})/$', views.comment, name = 'comment'),
    url(r'^user/(?P<username>.{1,50})/$', views.user, name = 'user'),
    url(r'^dataset/delete/(?P<dataset>[0-9]{1,11})/$', views.delete_dataset, name = 'delete_dataset'),
    url(r'^dataset/rate/(?P<dataset>[0-9]{1,11})/$', views.rate_dataset, name = 'rate_dataset'),
    url(r'^comment/delete/(?P<comment>[0-9]{1,11})/$', views.delete_comment, name = 'delete_comment'),
]
