from django_filters import rest_framework
from django_filters.rest_framework import FilterSet

from ..recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = rest_framework.CharFilter(lookup_expr="istartswith")

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

    class Meta:
        model = Recipe
        fields = ["author", "tags"]
