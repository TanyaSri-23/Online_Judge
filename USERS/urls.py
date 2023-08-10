from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.registerPage, name='register'),
    # path('activate/<uidb64>/<token>',views.activate,name='activate'), 

    path('login', views.loginUser, name='login'),
    path('logout', views.logoutUser, name='logout'),
    path('all_submissions/', views.allSubmissionPage, name='all_submissions'),


]