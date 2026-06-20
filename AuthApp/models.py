from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Profile specific data
    profile_picture_url = models.URLField(max_length=500, blank=True, null=True) # For ImageKit later
    bio = models.TextField(max_length=500, blank=True, null=True)
    social_link = models.URLField(max_length=255, blank=True, null=True) # <-- Added
    
    def __str__(self):
        return f"{self.user.username}'s Profile"