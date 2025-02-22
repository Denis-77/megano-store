from django.urls import path

from app_order.views import SetOrdersView, OrderView, PaymentAPIView


urlpatterns = [
    path('orders', SetOrdersView.as_view(), name='history'),
    path('order/<int:pk>', OrderView.as_view(), name='order'),

    path('payment/<int:pk>', PaymentAPIView.as_view(), name='payment'),

]
