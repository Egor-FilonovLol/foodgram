from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from recipes.constants import MAX_LENGTH


class User(AbstractUser):
    email = models.EmailField(verbose_name="почта",
                              unique=True,
                              max_length=MAX_LENGTH)
    username = models.CharField(
        max_length=150,
        verbose_name="Имя пользователя",
        unique=True,
        validators=[UnicodeUsernameValidator()]
    )
    first_name = models.CharField(max_length=MAX_LENGTH, verbose_name="имя")
    last_name = models.CharField(max_length=MAX_LENGTH, verbose_name="фамилия")
    avatar = models.ImageField(
        upload_to="users/", blank=True, default='', verbose_name="Аватар"
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return self.username
