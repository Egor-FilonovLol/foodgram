from django.core.validators import MinValueValidator
from django.db import models

from users.models import User
from recipes.constants import NAME_SLUG, MAX_LENGTH


class Tag(models.Model):
    name = models.CharField(
        max_length=NAME_SLUG, unique=True, verbose_name="название"
    )
    slug = models.SlugField(max_length=NAME_SLUG,
                            unique=True,
                            verbose_name="Слаг")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=MAX_LENGTH, verbose_name="Название")
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH, verbose_name="Ед измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_name_measurement_unit",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    name = models.CharField(max_length=MAX_LENGTH, verbose_name="название")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes"
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления", validators=[MinValueValidator(1)]
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания", db_index=True
    )
    image = models.ImageField(
        verbose_name="изображение рецепта",
        upload_to="recipes/images/",
        default=''
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientInRecipe",
        related_name="recipes",
        verbose_name="ингредиенты",
    )
    tags = models.ManyToManyField(Tag, related_name="recipes")
    text = models.TextField(verbose_name="текст")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-created",)


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name="ingredient_list",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name="ingredient_in_recipes",
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="количество", validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Количество ингредиента в рецепте"
        verbose_name_plural = "Количество ингредиентов в рецепте"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="unique_ingredients_recipe",
            )
        ]
        ordering = ("ingredient__name",)

    def __str__(self):
        return f"{self.ingredient.name} и {self.ingredient.measurement_unit}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name="favorites",
        on_delete=models.CASCADE,
        verbose_name="пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="любимые рецепты",
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "user"), name="unique_user_recipe"
            )
        ]
        ordering = ("recipe__name",)

    def __str__(self):
        return f"{self.user} и {self.recipe}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name="shopping_user",
        on_delete=models.CASCADE,
        verbose_name="пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="shopping_recipe",
        on_delete=models.CASCADE,
        verbose_name="рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "user"), name="unique_shoppingcart"
            )
        ]
        ordering = ("recipe__name",)


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        related_name="follow",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    user = models.ForeignKey(
        User,
        related_name="follower",
        on_delete=models.CASCADE,
        verbose_name="подписчие",
    )

    class Meta:
        verbose_name = "подписка"
        verbose_name_plural = "подписки"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "author"), name="unique_follow"
            )
        ]
        ordering = ("author__username",)
