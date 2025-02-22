from django.urls import path
from .views import (
    CatalogListView, CatalogView, LimitedView, PopularView, BannersView
)


urlpatterns = [
    path('categories/', CatalogListView.as_view(), name='categories'),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('products/limited/', LimitedView.as_view(), name='limited'),
    path('products/popular/', PopularView.as_view(), name='popular'),
    path('banners/', BannersView.as_view(), name='banners'),
]
