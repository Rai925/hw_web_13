from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from .forms import RegisterForm

def signupuser(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Ви успішно зареєструвалися!')
            return redirect('/')
    else:
        form = RegisterForm()
    return render(request, 'users/signup.html', {'form': form})
def signinuser(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, 'You have been logged in!')
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'users/signin.html', {'form': form})