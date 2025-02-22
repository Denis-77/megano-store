from rest_framework import serializers
from app_catalog.serializers import ProductSerializerForCatalog


class BasketSerializer(ProductSerializerForCatalog):
    count = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='count',
        source='basket'
    )

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result['count'] = result.pop('count')[0]
        return result


class AnonymBasket(ProductSerializerForCatalog):
    count = serializers.SerializerMethodField()

    def get_count(self, instance):
        return instance.count_in_basket
