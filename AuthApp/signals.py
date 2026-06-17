from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically creates a UserProfile when a new User is registered."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Saves the profile whenever the User object is saved."""
    instance.profile.save()
    
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from .models import UserProfile

# --- NEW: Global Email Uniqueness Enforcer ---
@receiver(pre_save, sender=User)
def enforce_unique_email(sender, instance, **kwargs):
    """
    Fires right before a User is saved to the database.
    Checks globally if the email already exists on another account.
    """
    if instance.email:
        # Check if this email exists on any account that IS NOT this specific user
        email_exists = User.objects.filter(email__iexact=instance.email).exclude(pk=instance.pk).exists()
        if email_exists:
            # This completely halts the database save operation
            raise ValidationError(f"A user with the email '{instance.email}' already exists.")

# --- Existing Profile Signals ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()    