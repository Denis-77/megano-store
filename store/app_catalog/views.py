import random

from django.db.models import Q, Count, Min

from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics

from .serializers import (
    CatalogItemSerializer, ProductSerializerForCatalog, BannerSerializer
)
from .models import CatalogItem
from app_products.models import Product

LIST_OF_PROMOTED = [5, 8, 9, 6, 10, 7]


class CatalogListView(generics.ListAPIView):
    serializer_class = CatalogItemSerializer

    def get_queryset(self):
        queryset = (
            CatalogItem.objects
            .filter(parent_category=None)
            .prefetch_related('catalog_item')
            .prefetch_related('item_image')
        )
        return queryset


class ListPagination(PageNumberPagination):
    page_size = 4
    page_query_param = 'currentPage'
    page_size_query_param = 'limit'
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'items': data,
            'currentPage': self.page.number,
            'lastPage': self.page.paginator.num_pages
        })


class CatalogView(generics.ListAPIView):
    pagination_class = ListPagination
    serializer_class = ProductSerializerForCatalog

    def get_queryset(self):

        search = self.request.GET['filter[name]']
        min_price = self.request.GET['filter[minPrice]']
        max_price = self.request.GET['filter[maxPrice]']
        free_delivery = self.request.GET['filter[freeDelivery]']
        available = self.request.GET['filter[available]']

        category = self.request.GET.get('category')
        sort = self.request.GET['sort']
        sort_type = self.request.GET['sortType']

        response_dict = dict(self.request.GET)
        tags = response_dict.get('tags[]')

        query_set = (
            Product.objects.filter(
                Q(price__gte=min_price) & Q(price__lte=max_price)
            )

            .annotate(Count('review'))
            .prefetch_related('tags')
            .prefetch_related('product_image')
        )

        if search:
            query_set = query_set.filter(title__icontains=search)

        if category:
            query_set = query_set.filter(category=category)

        if free_delivery == 'true':
            query_set = query_set.filter(free_delivery=True)

        if available == 'true':
            query_set = query_set.filter(count__gt=0)

        if tags:
            query_set = query_set.filter(tags__in=tags)

        sorting = 'price'

        if sort == 'reviews':
            sorting = 'review__count'
        elif sort == 'rating':
            sorting = 'rating'
        elif sort == 'date':
            sorting = 'date'

        if sort_type == 'dec':
            sorting = '-' + sorting

        query_set = query_set.order_by(sorting)

        return query_set


class LimitedView(generics.ListAPIView):
    serializer_class = ProductSerializerForCatalog

    queryset = (
        Product.objects
        .filter(count__in=[1, 2, 3])
        .annotate(Count('review'))
        .prefetch_related('tags')
        .prefetch_related('product_image')
    )[:8]


class PopularView(generics.ListAPIView):
    serializer_class = ProductSerializerForCatalog

    queryset = (
        Product.objects

        .annotate(Count('review'))
        .prefetch_related('tags')
        .prefetch_related('product_image')
        .order_by('-rating', '-sold')
    )[:8]


class BannersView(generics.ListAPIView):
    serializer_class = BannerSerializer

    def get_queryset(self):
        promoted = LIST_OF_PROMOTED
        if len(promoted) > 3:
            promoted = random.sample(promoted, k=3)
        queryset = (
            CatalogItem.objects
            .filter(id__in=promoted)
            .prefetch_related('item_image')
            .annotate(Min('product__price'))
        )
        return queryset
