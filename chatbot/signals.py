from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import DigitalIdentity

@receiver(post_save, sender=User)
def create_digital_identity(sender, instance, created, **kwargs):
    if created:
        DigitalIdentity.objects.create(user=instance)
