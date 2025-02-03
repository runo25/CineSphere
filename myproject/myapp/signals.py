# signals.py (correct import)
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile, Community
from django.contrib.auth import get_user_model  # Import your custom User model

User = get_user_model()  # Dynamically get the active User model

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        default_community = Community.objects.first()
        if default_community:
            UserProfile.objects.create(user=instance, community=default_community)
        else:
            # Handle missing community (e.g., log a warning)
            pass