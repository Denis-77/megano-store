import json

import rest_framework.serializers
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import CreateUserSerializer, UserSerializer
from .models import Profile, Avatar

from app_basket.models import BasketItem
from app_products.models import Product


def addition_basket_from_cookie_to_db(user, request):
    json_data: str | None = request.session.get('basket')
    if json_data:

        data: dict = json.loads(json_data)
        products = map(int, data.keys())

        basket_objs = (
            BasketItem.objects
            .filter(user=user, product__in=products)
            .select_related('product')
        )

        for basket_obj in basket_objs:
            product_id = str(basket_obj.product.id)
            max_count = basket_obj.product.count
            count_before = basket_obj.count
            new_count = count_before + data.pop(product_id)
            if new_count > max_count:
                new_count = max_count

            basket_obj.count = new_count
            basket_obj.save()

        while data:
            product_id, count = data.popitem()
            product = Product.objects.get(pk=product_id)
            max_count = product.count
            if count > max_count:
                count = max_count
            BasketItem.objects.create(
                user=user,
                product=product,
                count=count
            )


class LoginAPIView(APIView):

    def post(self, request):
        json_data = request.body.decode('utf-8')
        data = json.loads(json_data)

        user = authenticate(
            request, username=data['username'], password=data['password']
        )

        if user is not None:
            login(request, user)
            addition_basket_from_cookie_to_db(user=user, request=request)
            return Response({'message': 'successful operation'}, status=200)

        return Response({'message': f'unsuccessful operation'}, status=500)


class RegistrationAPIView(APIView):

    def post(self, request):

        data = list(request.data)
        data = json.loads(data[0])

        serializer = CreateUserSerializer(data=data)

        if serializer.is_valid():
            user = serializer.create(validated_data=data)
            login(request, user)
            addition_basket_from_cookie_to_db(user=user, request=request)
            return Response(
                {'message': 'successful operation'},
                status=200
            )

        return Response(
            {'message': f'unsuccessful operation {serializer.errors}'},
            status=500
        )


class LogoutAPIView(APIView):

    def post(self, request):
        logout(request)
        return Response({'message': 'successful operation'}, status=200)


class ProfileAPIView(APIView):

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(data=serializer.data, status=200)


    def post(self, request):
        data = request.data
        data['phone'] = ''.join(char for char in data['phone'] if char.isdigit())
        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            serializer.update(instance=request.user, validated_data=data)
            return Response({'message': 'successful operation'}, status=200)

        return Response(
            {'message': f'unsuccessful operation {serializer.errors}'},
            status=500
        )


class ChangePasswordAPIView(APIView):

    def post(self, request):
        data = request.data

        user = authenticate(
            request, username=request.user.username, password=data['currentPassword']
        )
        if user is not None:
            try:
                new_password = CreateUserSerializer.validate_password(value=data['newPassword'])
                user.set_password(new_password)
                user.save()
                return Response({'message': 'successful operation'}, status=200)

            except rest_framework.serializers.ValidationError as exc:
                return Response({'message': f'unsuccessful operation {exc.detail}'}, status=500)

        return Response({'message': f'unsuccessful operation: wrong password'}, status=500)


class AvatarAPIView(APIView):
    def post(self, request):
        profile = Profile.objects.filter(user=request.user)

        if profile:
            profile = profile.first()

            avatar = Avatar.objects.filter(profile=profile)
            if avatar:
                avatar = avatar.first()
                avatar.src = request.FILES['avatar']
                avatar.save()
            else:
                Avatar.objects.create(
                    profile=profile,
                    src=request.FILES['avatar'],
                    alt=profile
                )
            return Response({'message': 'successful operation: avatar was changed'}, status=200)
        return Response({'message': 'unsuccessful operation'}, status=500)
