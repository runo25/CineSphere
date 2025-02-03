# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Community

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Assign a default community (e.g., first Community object)
        default_community = Community.objects.first()
        UserProfile.objects.create(user=instance, community=default_community)