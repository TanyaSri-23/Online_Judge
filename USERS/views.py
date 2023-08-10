'''
List of Views:
- REGISTER PAGE: To register a new user.
- LOGIN PAGE: To login a registered user.
- LOGOUT PAGE: To logout a registered user.
- ACOOUNT SETTINGS PAGE : To update profile pic and full name.
- VERDICT PAGE: Shows the verdict to the submission.
- SUBMISSIONS PAGE: To view all the submissions made by current logged-in user.
- LEADERBOARD: Diplay the leaderboard.
'''
from django.core.mail import EmailMessage

from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_protect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str
from django.contrib.auth import authenticate, login

from .tokens import account_activation_token
from USERS.models import User, Submissions
from OJ.models import Problem, Testcase
from .forms import CreateUserForm, UpdateProfileForm
from datetime import datetime
from time import time

import os
import sys
import subprocess
from subprocess import PIPE
import os.path





# To register a new user


# To login a registered user
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.info(request, 'Username/Password is incorrect')

        context = {}
        return render(request, 'login.html', context)




def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user_username = form.cleaned_data.get('username')
            if User.objects.filter(username=user_username):
                messages.error(request,'Username already exist!')
                context = {'form': form}
                return redirect(request, 'register.html', context)

            user = form.save()
            user.is_active = True
            user.save()
            messages.success(request, 'Account created successfully!')

            username = form.cleaned_data.get('username')
            current_site = get_current_site(request)
            

            return redirect('login')

    else:
        form = CreateUserForm()
    context = {'form': form}
    return render(request, 'register.html', context)


# To login a registered user
# @require_POST  # Ensure the view only accepts POST requests
# @csrf_protect  # Apply CSRF protectio
def loginUser(request):
    if request.method=="POST":
        # check if user crediantials is true
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request,username=username, password=password)
        print(user)
        if user is not None:
            
            messages.success(request, "Sucessfully Logged in")
            login(request,user)
            return redirect("dashboard")
 
        else:
            return render(request, 'login.html')
    return render(request, 'login.html')

# To logout a registered user
def logoutUser(request):
    logout(request)
    return redirect('login')

# To activate user account via email verification
# def activate(request,uidb64,token):
#     try:
#         uid=force_str(urlsafe_base64_decode(uidb64))
#         user=User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user=None
  
#     if user is not None and account_activation_token.check_token(user,token):
#         user.is_active=True
#         user.save()
#         login(request,user)
#         return redirect('dashboard')
#     else:
#         messages.error(request,'Activation failed, Please try again!')
#         return render(request,'register.html')











# to update prfile pic and full name
# @login_required(login_url='login')
# def accountSettings(request):
#     form = UpdateProfileForm(instance=request.user)

#     if request.method == 'POST':
#         form = UpdateProfileForm(
#             request.POST, request.FILES, instance=request.user)
#         if form.is_valid():
#             form.save()

#     context = {'form': form}
#     return render(request, 'USERS/account_settings.html', context)





@login_required(login_url='login')
def allSubmissionPage(request):
    submissions = Submissions.objects.filter(user=request.user.id)
    return render(request, 'submission.html', {'submissions': submissions})