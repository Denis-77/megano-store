from rest_framework import serializers
from .models import (
    Product, Review, Image, Specification, Tag, SaleItem
)


class SpecificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Specification
        fields = ['name', 'value']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['name']


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ['src', 'alt']


class ReviewSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='first_name',
        source='user'
     )

    email = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='email',
        source='user'
    )

    class Meta:
        model = Review
        fields = 'author', 'email', 'text', 'rate', 'date'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if not instance.user.first_name:
            representation['author'] = instance.user.username
        return representation


class ProductSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format='%a %b %d %Y %H:%M:%S GMT%z (%Z)')
    images = ImageSerializer(many=True, read_only=True, source='product_image')
    reviews = ReviewSerializer(many=True, read_only=True, source='review_set')
    specifications = SpecificationSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'price', 'count', 'date', 'title',
            'description', 'free_delivery', 'rating',
            'specifications', 'tags', 'images', 'reviews'
        ]

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


class SalesSerializer(serializers.ModelSerializer):
    date_from = serializers.DateField(format='%m-%d')
    date_to = serializers.DateField(format='%m-%d')
    images = serializers.SerializerMethodField()
    id = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='id',
        source='product'
    )
    title = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='title',
        source='product'
    )
    price = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='price',
        source='product'
    )

    class Meta:
        model = SaleItem
        fields = [
            'id', 'sale_price', 'date_from', 'date_to',
            'title', 'price', 'images'
        ]

    def get_images(self, instance):
        list_serializers = []
        for image in instance.product.product_image.all():
            serializer = ImageSerializer(image)
            list_serializers.append(serializer.data)
        return list_serializers

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['price'] = float(representation.pop('price'))

        representation['salePrice'] = float(representation.pop('sale_price'))
        representation['dateFrom'] = representation.pop('date_from')
        representation['dateTo'] = representation.pop('date_to')

        return representation


class TagsSerializer(TagSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name']
