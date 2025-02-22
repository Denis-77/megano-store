import os

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.PositiveBigIntegerField(
        verbose_name='Phone number', null=True, blank=True, default=0
    )
    default_city = models.CharField(verbose_name='Delivery city', max_length=50, blank=True)
    default_address = models.CharField(verbose_name='Delivery address', max_length=255, blank=True)
    default_delivery_type = models.CharField(verbose_name='Type of delivery', max_length=255, blank=True)
    default_payment_type = models.CharField(verbose_name='Type of payment', max_length=255, blank=True)

    def __str__(self):
        return self.user.__str__()


def user_directory_path(instance, filename):
    return f'images/users/{instance.profile.id}/{filename}'


class Avatar(models.Model):
    src = models.ImageField('avatar image', upload_to=user_directory_path)
    alt = models.CharField(
        verbose_name='alternative text',
        max_length=70,
        default='image'
    )
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)


@receiver(pre_save, sender=Avatar)
def delete_old_image_file(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Avatar.objects.get(pk=instance.pk)
        old_image_path = old_instance.src.path
        if os.path.isfile(old_image_path):
            os.remove(old_image_path)


@receiver(post_delete, sender=Avatar)
def delete_image_file(sender, instance, **kwargs):
    if instance.src:
        image_path = instance.src.path
        if os.path.isfile(image_path):
            os.remove(image_path)
