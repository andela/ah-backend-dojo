from django.db import models
from authors.apps.authentication.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    
    # one to one relationship
    user = models.OneToOneField(
        User, to_field="username", on_delete=models.CASCADE
    )
    firstname = models.CharField(max_length=250, default='')
    lastname = models.CharField(max_length=250, default='')
    # display some info about a user
    bio = models.TextField(blank=True)
    # an optional profile image
    image = models.URLField(blank=True)
    birthday = models.CharField(max_length=50, default='')
    gender = models.CharField(max_length=50, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Creates a profile after user has been registered
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()