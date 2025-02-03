# myapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction, IntegrityError
from django.conf import settings
from .models import UserProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: UserProfile.objects.get_or_create(user=instance))
    else:
        try:
            # Try to save the related profile
            instance.userprofile.save()
        except UserProfile.DoesNotExist:
            transaction.on_commit(lambda: UserProfile.objects.get_or_create(user=instance))

            # If for some reason the profile is missing, create it after commit.
            transaction.on_commit(lambda: UserProfile.objects.create(user=instance))
