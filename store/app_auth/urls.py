from django.urls import path
from .views import (
    LoginAPIView, RegistrationAPIView,
    LogoutAPIView, ProfileAPIView, ChangePasswordAPIView,
    AvatarAPIView,
)


urlpatterns = [
    path('sign-in', LoginAPIView.as_view(), name='sign-in'),
    path('sign-up', RegistrationAPIView.as_view(), name='sign-up'),
    path('sign-out', LogoutAPIView.as_view(), name='sign-out'),
    path('profile', ProfileAPIView.as_view(), name='profile'),
    path('profile/password', ChangePasswordAPIView.as_view(), name='change-password'),
    path('profile/avatar', AvatarAPIView.as_view(), name='avatar')
]
