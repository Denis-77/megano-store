from django.contrib import admin
from .models import Profile, Avatar


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = 'id', 'user', 'phone'


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = 'id', 'src', 'alt', 'profile'
