import django_filters
from django_filters import rest_framework
from django_filters.rest_framework import FilterSet
from django_filters import rest_framework as django_filters
from .models import Ingredient, Recipe, Tag

class IngredientFilter(FilterSet):
    """Поиск по названию ингредиента"""

    name = rest_framework.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )
    author = django_filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']