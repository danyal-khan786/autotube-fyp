from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Welcome to AutoTube AI.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
        
    return render(request, 'AuthApp/register.html', {'form': form})

from django.contrib.auth.decorators import login_required
from .forms import UserAccountForm, UserProfileForm
from .models import UserProfile

@login_required
def edit_profile(request):
    """Handles updating both the User Account and the User Profile simultaneously."""
    
    # Failsafe: Ensure the profile exists just in case the signal missed it
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        account_form = UserAccountForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        if account_form.is_valid() and profile_form.is_valid():
            account_form.save()
            profile_form.save()
            messages.success(request, "Your account and profile have been updated.")
            return redirect('edit_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        account_form = UserAccountForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'account_form': account_form,
        'profile_form': profile_form
    }
    return render(request, 'AuthApp/edit_profile.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserAccountForm

@login_required
def edit_account(request):
    """Standalone view strictly for updating the native Django User Account."""
    if request.method == 'POST':
        form = UserAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account details have been updated successfully.")
            return redirect('edit_account')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserAccountForm(instance=request.user)

    return render(request, 'AuthApp/edit_account.html', {'form': form})







