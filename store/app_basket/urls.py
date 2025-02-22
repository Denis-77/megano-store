from django.urls import path
from .views import (
    BasketAPIView
)


urlpatterns = [
    path('basket', BasketAPIView.as_view(), name='basket'),

]
