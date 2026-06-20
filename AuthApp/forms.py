# created manually!
from django import forms
from django.contrib.auth.models import User
from .models import *

class UserAccountForm(forms.ModelForm):
    """Strictly handles the native Django User table (The Account)."""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email address is already in use by another account.")
        return email


class UserProfileForm(forms.ModelForm):
    """Strictly handles the custom UserProfile table (The Profile)."""
    class Meta:
        model = UserProfile
        fields = ['bio', 'social_link'] # We will handle profile_picture_url explicitly when we build the ImageKit flow
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about your channel...'}),
            'social_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtube.com/@yourchannel'}),
        }
        

from django import forms
from django.contrib.auth.models import User

class UserAccountForm(forms.ModelForm):
    """Strictly handles the native Django User table (The Account)."""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        """Form-level validation to prevent duplicate emails."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email address is already in use by another account.")
        return email






















        