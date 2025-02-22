import json

from django.db.models import Count, Prefetch

from rest_framework.response import Response
from rest_framework.views import APIView

from app_products.models import Product
from .serializers import BasketSerializer, AnonymBasket

from .models import BasketItem


class BasketAPIView(APIView):

    def post(self, request):

        data = request.data
        user = request.user
        product = Product.objects.get(pk=data['id'])
        count = data['count']

        if user.is_authenticated:

            basket_obj = BasketItem.objects.filter(user=user, product=product)
            if basket_obj:
                basket_obj = basket_obj.get()
                if product.count < basket_obj.count + count:
                    return Response('too many goods', status=500)

                basket_obj.count += count
                basket_obj.save()

            else:
                if product.count < count:
                    return Response('too many goods', status=500)
                BasketItem.objects.create(
                    user=user,
                    product=product,
                    count=count
                )

        else:

            old_data: str | None = request.session.get('basket')
            product_id = str(data['id'])
            total = data['count']
            data = {product_id: total}

            if product.count < total:
                return Response('too many goods', status=500)

            if old_data:
                old_data: dict = json.loads(old_data)
                total += old_data.get(product_id, 0)

                if product.count < total:
                    return Response('too many goods', status=500)

                data = old_data.copy()
                data[product_id] = total

            json_data = json.dumps(data)
            request.session['basket'] = json_data
        return self.get(request=request)

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            basket_objects = BasketItem.objects.filter(user=user)
            data = (
                Product.objects
                .annotate(Count('review'))
                .prefetch_related(Prefetch(lookup='basket', queryset=basket_objects))
                .prefetch_related('tags')
                .prefetch_related('product_image')
                .filter(basket__user=user)
            )
            serializer = BasketSerializer(data, many=True)
            return Response(serializer.data, status=200)

        else:

            json_data: str | None = request.session.get('basket')
            if not json_data:
                return Response('', status=200)
            data: dict = json.loads(json_data)
            products = map(int, data.keys())
            queryset = (
                Product.objects
                .annotate(Count('review'))
                .prefetch_related('tags')
                .prefetch_related('product_image')
                .filter(id__in=products)
            )
            for item in queryset:
                item.count_in_basket = data[str(item.id)]
            serializer = AnonymBasket(queryset, many=True)
            return Response(serializer.data, status=200)

    def delete(self, request):

        data = request.data

        user = request.user
        product = Product.objects.get(pk=data['id'])
        count = data['count']

        if user.is_authenticated:

            basket_obj = BasketItem.objects.get(user=user, product=product)
            if not basket_obj:
                return Response('wrong product', status=500)

            if basket_obj.count <= count:
                basket_obj.delete()

            else:
                basket_obj.count -= count
                basket_obj.save()

        else:

            product_id = str(data['id'])
            count = data['count']

            data: str | None = request.session.get('basket')
            if not data:
                return Response('miss data', status=500)

            data: dict = json.loads(data)

            if data[product_id] > count:
                data[product_id] -= count
            else:
                data.pop(product_id)

            json_data = json.dumps(data)
            request.session['basket'] = json_data
        return self.get(request=request)
