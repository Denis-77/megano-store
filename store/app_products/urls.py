from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, ReviewAPIView, SalesAPIView, TagsAPIView
)

routers = DefaultRouter()
routers.register('product', ProductViewSet)

urlpatterns = [
    path('', include(routers.urls)),
    path('product/<int:pk>/reviews', ReviewAPIView.as_view(), name='make_review'),
    path('sales/', SalesAPIView.as_view(), name='sales'),
    path('tags/', TagsAPIView.as_view(), name='tags'),

]
