from django.shortcuts import render, redirect
from .form import UserLoginForm, UserRegistrationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


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

def profile(request):
    return render(request, 'accounts/profile.html')  # Redirect to the profile page after successful login

@login_required
def profile_view(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        # Update user
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('profile') # Replace 'profile' with your actual URL name
        
    return render(request, 'accounts/profile.html')


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) # Keep user logged in
            messages.success(request, "Password updated successfully!")
            return redirect('profile')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
            return redirect('profile')
            
    return redirect('profile')