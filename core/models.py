from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        default='profile_pictures/default.jpg'
    )
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a Profile only if the User is newly created
        Profile.objects.create(user=instance)
    else:
        # Save the Profile only if it already exists
        if hasattr(instance, 'profile'):
            instance.profile.save()

# filepath: d:\Django2.0\nana rajkot\school_management\core\management\commands\remove_duplicate_profiles.py
from django.core.management.base import BaseCommand
from core.models import Profile
from django.db.models import Count

class Command(BaseCommand):
    help = 'Remove duplicate profiles'

    def handle(self, *args, **kwargs):
        duplicates = Profile.objects.values('user').annotate(count=Count('id')).filter(count__gt=1)

        for duplicate in duplicates:
            profiles = Profile.objects.filter(user_id=duplicate['user'])
            profiles.exclude(id=profiles.first().id).delete()

        self.stdout.write(self.style.SUCCESS('Duplicate profiles removed successfully.'))

