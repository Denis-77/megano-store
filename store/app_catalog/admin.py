from django.contrib import admin

from app_catalog.models import CatalogItem, Image

class ImageInline(admin.TabularInline):
    model = Image

@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    list_display = (
            'id', 'title', 'parent_category', 'item_image'
    )
    inlines = [ImageInline, ]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = 'id', 'src', 'alt',
