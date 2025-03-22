from django.contrib import admin
from app_products.models import (
    Product, Tag, Specification, Image, Review, SaleItem
)

class ImageInline(admin.TabularInline):
    model = Image

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'price', 'description', 'date',
        'rating', 'count', 'free_delivery', 'category',
        'sold'
    )
    inlines = [ImageInline, ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = 'id', 'name'


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'value'


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = 'id', 'src', 'alt', 'product'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = 'id', 'product', 'user', 'less_text', 'rate', 'date'

    def less_text(self, obj):
        if len(obj.text) > 30:
            return obj.text[:30] + '...'
        return obj.text


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = 'id', 'product', 'sale_price', 'date_from', 'date_to'
