from rest_framework import serializers
from .models import Profile, User, Avatar


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'username', 'password']

    @staticmethod
    def validate_password(value: str):
        if any([
            len(value) < 8,
            value.isalpha(),
            value.isdigit()
        ]):
            raise serializers.ValidationError(
                'The password must contain at least '
                '8 characters, 1 number and 1 letter.'
            )
        return value

    def create(self, validated_data):
        user = User(
            first_name=validated_data['name'],
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()

        profile = Profile(
            user=user
        )
        profile.save()
        return user


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avatar
        fields = ['src', 'alt']


class ProfileSerializer(serializers.ModelSerializer):
    avatar = AvatarSerializer(required=False)

    class Meta:
        model = Profile
        fields = ['user', 'phone', 'avatar']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'email', 'profile']

    def update(self, instance, validated_data):
        instance.first_name = validated_data['fullName']
        instance.email = validated_data['email']
        instance.save()

        profile = Profile.objects.get(user=instance)
        profile.phone = validated_data['phone']

        profile.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        profile_data = representation.pop('profile')
        profile_data.pop('user')
        representation.update(profile_data)

        # Because of frontend
        representation['fullName'] = representation['first_name']
        representation['phone'] = str(representation['phone'])

        return representation
