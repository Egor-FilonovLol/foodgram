import django_filters
from django_filters import rest_framework
from django_filters.rest_framework import FilterSet

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name",
                                     lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeFilter(rest_framework.FilterSet):
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
    )
    author = rest_framework.NumberFilter(field_name="author__id")
    is_favorited = rest_framework.BooleanFilter(
        method='is_recipe_in_favorites_filter')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='is_recipe_in_shopping_cart_filter')

    def is_recipe_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(
                shopping_recipe__user=user
            )
        else:
            return queryset

    def is_recipe_in_favorites_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorited_by__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")
