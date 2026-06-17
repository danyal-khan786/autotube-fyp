from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # We will store the ImageKit CDN URL here later
    profile_picture_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Extra profile fields
    bio = models.TextField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"