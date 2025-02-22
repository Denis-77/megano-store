from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from .serializers import (
    ProductSerializer, SalesSerializer, TagsSerializer
)
from .models import Product, Review, SaleItem, Tag


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ReviewAPIView(APIView):

    def post(self, request, pk):
        queryset = Product.objects.filter(id=pk)
        if queryset and request.user.is_authenticated:
            product = queryset.first()
            data = request.data
            Review.objects.create(
                product=product,
                text=data['text'],
                rate=data['rate'],
                user=request.user
            )
            return Response({'message': 'successful operation'}, status=200)

        return Response({'message': 'unsuccessful operation'}, status=500)


class SalesPagination(PageNumberPagination):
    page_size = 4
    page_query_param = 'currentPage'
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'items': data,
            'currentPage': self.page.number,
            'lastPage': self.page.paginator.num_pages
        })


class SalesAPIView(ListAPIView):
    serializer_class = SalesSerializer
    pagination_class = SalesPagination

    def get_queryset(self):
        queryset = (
            SaleItem.objects
            .select_related('product')
            .prefetch_related('product__product_image')
            .order_by('id')
        )
        return queryset


class TagsAPIView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
