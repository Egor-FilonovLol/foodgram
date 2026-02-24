from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from .models import Tag, Ingridient
from django.contrib.auth.hashers import make_password
from drf_base64.fields import Base64ImageField

User = get_user_model()


class UserCreateSerializer(ModelSerializer):
    email = serializers.CharField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(min_length=8,
                                     write_only=True,
                                     required=True,
                                     style={'input_type': 'password'}
                                     )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user


class UserListSerializer(ModelSerializer):
    email = serializers.CharField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',)


class ChangeUserPasswordSerializer(Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(detail='Неправильный пароль')
        return value

    def validate_new_password(self, value):
        user = self.context['request'].user
        if user.check_password(value):
            raise serializers.ValidationError(detail='Новый пароль != текущему паролю')
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user
        user.set_password(validated_data['new_password'])
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = ('id', 'name', 'measurement_unit')


class AvatarSerializer(Serializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
