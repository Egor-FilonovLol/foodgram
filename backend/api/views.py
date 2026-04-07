from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter, IngredientFilter
from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from .pagination import UserPagination
from .permission import RecipePermission
from .serializers import (
    AvatarSerializer,
    ChangeUserPasswordSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    RecipeSubscribeSerializer,
    SubscribeSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserListSerializer,
)
from rest_framework.viewsets import ReadOnlyModelViewSet

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = UserPagination

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserListSerializer

    def get_permissions(self):
        if self.action in ["create", "list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(methods=["post"], detail=False)
    def set_password(self, request):
        serializer = ChangeUserPasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["get"], detail=False)
    def me(self, request):
        serializer = UserListSerializer(
            request.user, context={"request": request}
        )
        return Response(serializer.data)

    @action(methods=["put", "delete"], detail=False, url_path="me/avatar")
    def me_avatar(self, request):
        if request.method == "PUT":
            if not request.data.get("avatar"):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = AvatarSerializer(
                instance=request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if request.user.avatar:
                avatar_url = request.build_absolute_uri(
                    request.user.avatar.url
                )
                return Response(
                    {"avatar": avatar_url}, status=status.HTTP_200_OK
                )
            return Response(
                {"avatar": None}, status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == "DELETE":
            if request.user.avatar:
                request.user.avatar.delete(save=False)
            request.user.avatar = None
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET"], detail=False, url_path="subscriptions")
    def get_subscribe(self, request):
        queryset = User.objects.filter(follower__user=request.user)
        page = self.paginate_queryset(queryset)
        recipes_limit = request.query_params.get("recipes_limit")
        if page is not None:
            serializer = SubscribeSerializer(
                page,
                many=True,
                context={"request": request, "recipes_limit": recipes_limit},
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeSerializer(
            queryset,
            many=True,
            context={"request": request, "recipes_limit": recipes_limit},
        )
        return Response(serializer.data)

    @action(methods=["DELETE", "POST"], detail=True, url_path="subscribe")
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, id=pk)
        change_subscribtion_status = Follow.objects.filter(
            user=user.id, author=author.id
        )
        if request.method == "POST":
            if user == author:
                return Response(
                    {"errors": ["Вы  нее можете подписаться на себя"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if change_subscribtion_status.exists():
                return Response(
                    {"errors": ["ввы уже подписаны на этого автора"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = UserListSerializer(
                author, context={"request": request}
            )
            Follow.objects.create(user=user, author=author)
            data = serializer.data
            recipes = author.recipes.all()
            recipes_limit = request.query_params.get("recipes_limit")
            if recipes_limit:
                recipes = recipes[: int(recipes_limit)]
            recipes_data = RecipeSubscribeSerializer(
                recipes, many=True, context={"request": request}
            ).data
            data["recipes"] = recipes_data
            data["recipes_count"] = author.recipes.count()
            return Response(data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if change_subscribtion_status.exists():
                change_subscribtion_status.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"error": ["вы не были подписаны"]},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = UserPagination
    permission_classes = (RecipePermission,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = Recipe.objects.all()
        queryset = self.filter_queryset(queryset)
        queryset = queryset.distinct()
        queryset = queryset.annotate(
            favorites_count=Count("favorited_by", distinct=True)
        )
        queryset = queryset.select_related("author").prefetch_related(
            "tags", "ingredient_list__ingredient"
        )
        return queryset

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return RecipeCreateSerializer
        return RecipeReadSerializer

    @action(methods=["get"], detail=True, url_path="get-link")
    def get_short_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        short_link = request.build_absolute_uri(f"/s/{recipe.id}/")
        return Response({"short-link": short_link})

    @action(methods=["POST", "DELETE"], detail=True, url_path="favorite")
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == "POST":
            if Favorite.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {"errors": ["этот рецепт уже в избранном"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeSubscribeSerializer(
                recipe, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            obj = Favorite.objects.filter(user=request.user, recipe=recipe)
            if not obj.exists():
                return Response(
                    {"errors": ["Рецепт отсутствует в избранном"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST", "DELETE"], detail=True)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == "DELETE":
            obj = ShoppingCart.objects.filter(user=request.user, recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": ["Рецепт отсутствует в корзине"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.method == "POST":
            if ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {"errors": ["рецепт уже в корзине"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeSubscribeSerializer(
                recipe, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=["GET"], detail=False, url_path="download_shopping_cart")
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientInRecipe.objects.filter(
                recipe__shopping_recipe__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_sum=Sum("amount"))
        )

        shopping_cart = []
        for ingredient in ingredients:
            shopping_cart += (
                f"{ingredient['ingredient__name']}"
                f"{ingredient['ingredient__measurement_unit']} -"
                f"{ingredient['total_sum']}\n"
            )
        return HttpResponse(shopping_cart, content_type="text/plain")

    def partial_update(self, request, *args, **kwargs):
        if "ingredients" not in request.data:
            return Response(
                {"ingredients": ["поле ingredients обязательно"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if "tags" not in request.data:
            return Response(
                {"tags": ["поле теги обязательно"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().partial_update(request, *args, **kwargs)
