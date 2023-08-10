from django.contrib import admin
from django.urls import path,include
from OJ import views

urlpatterns = [
    
    path ('', views.dashboard, name='dashboard'),
    # path('login', views.loginUser, name='login'),
    path('problem/<int:problem_id>/', views.prob_description, name='prob_description'),
    path('verdict/<int:problem_id>/', views.verdict, name='verdict'),
    # path('logout', views.logoutUser, name='logout'),
    # path('submit/', views.submit_code, name='submit_code'),




]
