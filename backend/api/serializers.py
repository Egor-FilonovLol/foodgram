from djoser.serializers import \
    UserCreateSerializer as DjoserCreateUserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from users.models import User

from .models import (Favorite, Follow, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


class UserCreateSerializer(DjoserCreateUserSerializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    def validate_username(self, value):
        import re

        if not re.fullmatch(r"^[\w.@+-]+\Z", value):
            raise serializers.ValidationError(
                "Нельзя использовать " "такие символы"
            )
        return value

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "id",
        )


class UserListSerializer(ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "id",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()

    def get_avatar(self, obj):
        request = self.context.get("request")
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class ChangeUserPasswordSerializer(Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(detail="Неправильный пароль")
        return value

    def validate_new_password(self, value):
        user = self.context["request"].user
        if user.check_password(value):
            raise serializers.ValidationError(
                detail="Новый пароль не должен "
                "совпадать с  текущем паролекм"
            )
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class AvatarSerializer(ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientInRecipeCreateSerializer(Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserListSerializer(read_only=True)
    ingredients = IngredientInRecipeReadSerializer(
        source="ingredient_list", many=True, read_only=True
    )
    image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "tags",
            "author",
            "ingredients",
            "image",
            "is_favorited",
            "is_in_shopping_cart",
            "cooking_time",
            "text",
        )

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipeCreateSerializer(ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    name = serializers.CharField(max_length=256)
    text = serializers.CharField()
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "tags",
            "ingredients",
            "image",
            "cooking_time",
            "text",
        )

    def validate_ingredients(self, data):
        if not data:
            raise serializers.ValidationError("Не может быть пустым список!")
        ingredient_id = [item["id"].id for item in data]
        if len(ingredient_id) != len(set(ingredient_id)):
            raise serializers.ValidationError(
                "Ингредиенты не могут " "повторяться.."
            )
        return data

    def validate_tags(self, data):
        if not data:
            raise serializers.ValidationError(
                "Ошибка, в связи с " "отсутствием тегов"
            )
        if len(data) != len(set(data)):
            raise serializers.ValidationError(
                "ошибка, не может быть " "разное количество"
            )
        return data

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance, context={"request": self.context.get("request")}
        )

        return serializer.data

    def create(self, validated_data):
        author = self.context.get("request").user
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        for ingredient in ingredients_data:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient["id"],
                amount=ingredient["amount"],
            )

        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags")
        instance.tags.clear()
        ingredients_data = validated_data.pop("ingredients")
        instance.ingredient_list.all().delete()
        instance = super().update(instance, validated_data)
        instance.tags.set(tags_data)
        for ingredient in ingredients_data:
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient["id"],
                amount=ingredient["amount"],
            )

        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Favorite
        fields = ("id", "name", "cooking_time", "image")


class ShoppingCartSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = ShoppingCart
        fields = ("id", "name", "image", "cooking_time")


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class SubscribeSerializer(UserListSerializer):
    recipes = serializers.SerializerMethodField(
        read_only=True, method_name="get_recipes"
    )
    recipes_count = serializers.SerializerMethodField(
        read_only=True, method_name="get_recipes_count"
    )

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )

    def get_recipes_count(self, obj):
        recipes_count = obj.recipes.count()
        return recipes_count

    def get_recipes(self, obj):
        request = self.context.get("request")
        if not request:
            return []
        recipes = obj.recipes.all().order_by("-id")
        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        return RecipeSubscribeSerializer(
            recipes, many=True, context={"request": request}
        ).data
