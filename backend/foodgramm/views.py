from rest_framework import viewsets
from .models import Tag, Ingredient, Recipe, Favorite, ShoppingCart, IngredientInRecipe, Follow
from .serializers import TagSerializer, IngredientSerializer, UserCreateSerializer, UserListSerializer,ChangeUserPasswordSerializer, RecipeReadSerializer, RecipeCreateSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import filters
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from .pagination import UserPagination
from rest_framework.decorators import action
from .serializers import AvatarSerializer, FavoriteSerializer,ShoppingCartSerialzier
from .permission import RecipePermission
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse
User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    permission_classes = (AllowAny,)
    search_fields = ('name',)


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = UserPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserListSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(methods=['post'], detail=False)
    def set_password(self, request):
        serializer = ChangeUserPasswordSerializer(data=request.data,
                                                  context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def me(self, request):
        serializer = UserListSerializer(request.user,
                                        context={'request': request})
        return Response(serializer.data)

    @action(methods=['put', 'delete'], detail=False, url_path='me/avatar')
    def me_avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarSerializer(instance=request.user,
                                          data=request.data,
                                          partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if request.user.avatar:
                avatar_url = request.build_absolute_uri(request.user.avatar.url)
                return Response({'avatar': avatar_url},
                                status=status.HTTP_200_OK)
            return Response({'avatar': None},
                            status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            if request.user.avatar:
                request.user.avatar.delete(save=False)
            request.user.avatar = None
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

# МОИ ПОДПИСКИ ОСТАЛСОЬ
    @action(methods=['DELETE', 'POST'], detail=True, url_path='subscribe')
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, id=pk)
        change_subscribtion_status = Follow.objects.filter(user=user.id,
                                                           author=author.id)
        if request.method == 'POST':
            if user == author:
                return Response('пытаетесь подписаться на самого себя', 
                                status=status.HTTP_400_BAD_REQUEST)
            if change_subscribtion_status.exists():
                return Response('вы уже подписаны на автора',
                                status=status.HTTP_400_BAD_REQUEST)
            subscribe = Follow.objects.create(user=user, author=author)
            subscribe.save()  # посмотреть что делает метод
            return Response(f'вы подписаланись на {author}',
                            status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if change_subscribtion_status.exists():
                change_subscribtion_status.delete()
                return Response(f'вы отписались от {author}',
                                status=status.HTTP_204_NO_CONTENT)
            return Response(f'вы не были подписаны на {author}',
                            status=status.HTTP_400_BAD_REQUEST)

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = UserPagination
    permission_classes = (RecipePermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'is_favorited', 'is_in_shopping_cart',)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return RecipeCreateSerializer
        return RecipeReadSerializer

    @action(methods=['get'], detail=True, url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        short_link = request.build_absolute_uri(f'/s/{recipe.id}/')
        return Response({'short-link': short_link})

    @action(methods=['POST', 'DELETE'], detail=True, url_path='favorite')
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(user=request.user,
                                        recipe=recipe).exists():
                return Response({'error': 'этот обджект уже существует'})
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            obj = Favorite.objects.filter(recipe=recipe, id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'неверно'},  # прописать более ясно
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'DELETE':
            obj = ShoppingCart.objects.filter(user=request.user,
                                                recipe=recipe)
            if obj.exists():
                obj.delete() 
                return Response(status=status.HTTP_204_NO_CONTENT)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=request.user, recipe=recipe).exists():
                return Response({'error': 'уже существует таким'})
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = ShoppingCartSerialzier(recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED) 
        # serializer data
        # istance
        # как работает фильтр ___
        # request.user когда надо передавать 
        # objects.

    @action(methods=['GET'], detail=False, url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_recipe__user=request.user).values(
                'ingredient__name',
                'ingredient__measurement_unit'
        ).annotate(total_sum=Sum('amount'))

        shopping_cart = []
        for ingredient in ingredients:
            shopping_cart += (
                f"{ingredient['ingredient__name']}"
                f"{ingredient['ingredient__measurement_unit']} -"
                f"{ingredient['total_sum']}\n"
            )
        return HttpResponse(shopping_cart, content_type='text/plain')  # возможно придется добавлять Content-Disposition
