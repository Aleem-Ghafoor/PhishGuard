from django.shortcuts import render, redirect
from .form import UserLoginForm, UserRegistrationForm
from django.contrib.auth import login, logout


def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page after successful registration
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard after successful login
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})
 
def logout_user(request):
    if request.method == 'POST':
        logout(request)
    return redirect('home')  # Redirect to the login page after logout