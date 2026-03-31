from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(verbose_name='почта', unique=True,
                              max_length=255)
    username = models.CharField(max_length=150,
                                verbose_name='Имя пользователя',
                                unique=True,)
    first_name = models.CharField(max_length=150, verbose_name='имя')
    last_name = models.CharField(max_length=150, verbose_name='фамилия')
    avatar = models.ImageField(
        upload_to='users/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
