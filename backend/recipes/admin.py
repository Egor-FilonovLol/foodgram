from django.contrib.admin import register, ModelAdmin
from .models import (
    IngredientInRecipe, Recipe, Ingredient,
    ShoppingCart, Tag, Favorite, Follow
)


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('id', 'name', 'author', 'cooking_time', 'tags',)
    search_fields = ('name', 'author__name',)
    list_filter = ('tags',)

    def favorited_count(self, obj):
        return obj.favorited_by.count()
    favorited_count.short_description = 'в избранном'


@register(IngredientInRecipe)
class IngredientInRecipeAdmin(ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount',)


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)


@register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ('author', 'user',)
