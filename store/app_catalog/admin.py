from django.contrib import admin

from .models import CatalogItem, Image


@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    list_display = (
            'id', 'title', 'parent_category'
    )


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = 'id', 'src', 'alt',
