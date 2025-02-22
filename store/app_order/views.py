from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from app_order.models import Order, OrderProduct
from app_products.models import Product
from app_basket.models import BasketItem
from app_order.serializers import OrderSerializer


class OrderView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):

        queryset = (
            Order.objects.all()
            .prefetch_related('order_product__product__tags')
            .prefetch_related('order_product__product__product_image')
            .prefetch_related('order_product__product__review_set')
        )
        return queryset

    def post(self, request, pk):
        data = request.data
        profile = request.user.profile
        order = Order.objects.get(id=pk)

        order.status = 'Waiting for payment'

        order.delivery_type = profile.default_delivery_type = data['deliveryType']
        order.payment_type = profile.default_payment_type = data['paymentType']
        order.city = profile.default_city = data['city']
        order.address = profile.default_address = data['address']

        order.save()
        profile.save()

        return Response(
            {"orderId": pk},
            status=200
        )


class SetOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = (
            Order.objects.all().filter(user=request.user)
            .prefetch_related('order_product')
            .prefetch_related('order_product__product')
            .prefetch_related('order_product__product__tags')
            .prefetch_related('order_product__product__product_image')
            .prefetch_related('order_product__product__review_set')
        )
        serializer = OrderSerializer(queryset, many=True)
        return Response(data=serializer.data)

    def post(self, request):
        data = request.data
        products_dict = {}
        total_price = 0
        for product in data:
            total_price += product['price'] * product['count']
            products_dict[product['id']] = product['count']
        total_price = round(total_price, 2)

        products = list(products_dict.keys())

        products = Product.objects.filter(id__in=products)
        user = request.user

        order_for_current_user = Order.objects.create(
            user=user,
            total_cost=total_price,
            delivery_name=user.first_name,
            delivery_email=user.email,
            delivery_phone=user.profile.phone,
            city=user.profile.default_city,
            address=user.profile.default_address,
            delivery_type=user.profile.default_delivery_type,
            payment_type=user.profile.default_payment_type,
            status='Products selected'
        )

        for product in products:
            count = products_dict[product.id]
            OrderProduct.objects.create(
                order=order_for_current_user,
                product=product,
                count=count
            )

        BasketItem.objects.filter(user=user).delete()
        return Response(
            {"orderId": order_for_current_user.id},
            status=200
        )


class PaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        data = request.data
        order = Order.objects.get(id=pk)
        order.status = 'Waiting for approve from the payment system'
        order.save()
        if not data['number'].isdigit():
            return Response(data={'message': 'cart number must be digits'}, status=500)
        last_symbol = data['number'][-1]
        if len(data['number']) > 8 or int(last_symbol) % 2:
            return Response(data={'message': 'bed number'}, status=500)

        return Response(status=200)
