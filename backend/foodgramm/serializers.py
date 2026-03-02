from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, Serializer, ValidationError
from rest_framework import serializers
from .models import Tag, Ingridient, User
from django.contrib.auth.hashers import make_password
from drf_base64.fields import Base64ImageField
from djoser.serializers import UserCreateSerializer as DjoserCreateUserSerializer


class UserCreateSerializer(DjoserCreateUserSerializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(min_length=8,
                                     write_only=True,
                                     required=True,
                                     style={'input_type': 'password'}
                                     )

    def validate_username(self, value):
        import re
        if not re.fullmatch(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError('Нельзя использовать такие символы')
        return value

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password',
                  'id',)


class UserListSerializer(ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'id',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        return False

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None


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
            raise serializers.ValidationError(detail='Новый пароль не должен совпадать с  текущем паролекм')
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
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


class AvatarSerializer(ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
