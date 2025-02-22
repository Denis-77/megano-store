from rest_framework import serializers
from .models import CatalogItem, Image
from app_products.serializers import TagsSerializer
from app_products.serializers import ImageSerializer as ImageProdSerializer
from app_products.models import Product


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ['src', 'alt']


class CatalogItemSerializer(serializers.ModelSerializer):
    item_image = ImageSerializer()
    catalog_item = serializers.SerializerMethodField()

    class Meta:
        model = CatalogItem
        fields = [
            'id', 'title', 'item_image',
            'catalog_item'
        ]

    def get_catalog_item(self, instance):
        if instance.catalog_item.exists():
            children_serializer = CatalogItemSerializer(instance.catalog_item, many=True)
            return children_serializer.data
        return []

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = representation.pop('item_image')
        representation['subcategories'] = representation.pop('catalog_item')
        return representation


class ProductSerializerForCatalog(serializers.ModelSerializer):
    date = serializers.DateTimeField(format='%a %b %d %Y %H:%M:%S GMT%z (%Z)')
    images = ImageProdSerializer(many=True, read_only=True, source='product_image')
    reviews = serializers.SerializerMethodField()
    tags = TagsSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'price', 'count', 'date', 'title',
            'description', 'free_delivery', 'rating',
            'tags', 'images', 'reviews', 'category'
        ]

    def get_reviews(self, instance):
        return instance.review__count

    def to_representation(self, instance):

        representation = super().to_representation(instance)

        representation['price'] = float(representation.pop('price'))
        full_descr = representation.pop('description')
        representation['fullDescription'] = full_descr
        if len(full_descr) > 20:
            representation['description'] = full_descr[:20] + '...'

        representation['freeDelivery'] = representation.pop('free_delivery')
        representation['rating'] = float(representation.pop('rating'))

        return representation


class BannerSerializer(serializers.Serializer):
    item_image = ImageSerializer()

    class Meta:
        model = CatalogItem
        fields = [
            'id', 'title', 'item_image',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['images'] = [representation.pop('item_image')]
        representation['id'] = instance.id
        representation['title'] = instance.title
        representation['price'] = instance.product__price__min
        representation['category'] = instance.id
        return representation
