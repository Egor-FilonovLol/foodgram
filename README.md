# Foodgram

Продуктовый помощник — платформа для публикации кулинарных рецептов, управления подписками и генерации списка покупок.

## 📋 Описание

Финальный проект курса по backend-разработке от **Яндекс Практикума**.

Платформа предоставляет REST API и интерфейс для:
- Публикации и просмотра кулинарных рецептов
- Подписки на авторов
- Добавления рецептов в избранное
- Автоматической генерации списка ингредиентов для одного или нескольких выбранных блюд

Проект контейнеризирован с помощью **Docker** и готов к развертыванию.

## 🛠️ Технологии

- Python 3.9+
- Django 3.2
- Django REST Framework (DRF)
- Djoser (аутентификация)
- PostgreSQL
- Docker / Docker Compose
- Nginx
- Gunicorn


## Функционал

1. Выполнить GET-запрос к эндпоинту ``/api/tags/``: Получение всех тегов
Ответ запроса

```

[

    {
    
        "id": 1,
        "name": "tag1",
        "slug": "slug1"
    
    },
    
    {
        "id": 2,
        "name": "tag2",
        "slug": "slug2"
    
    },
    
    {
        "id": 3,
        "name": "tag3",
        "slug": "slug3"
    
    }
]

```


2. Выполнить POST-запрос к эндпоинту `` /api/auth/token/login/ ``:
```

{
    "email": {{email}},
    "password": {{password}}
}

```

Результат запроса: 


```

{
    "auth_token": "token"
}
```


## Установка проекта

---

1. Клонировать репозиторий
`` 
git clone https://github.com/Egor-FilonovLol/foodgram.git
``

2. Перейти в репозиторий
``
cd foodgram
cd infra
``
Запуск проекта через Docker

Установите Docker, используя инструкции с официального сайта



## Создать файл .env в папке проекта:
``` 
POSTGRES_USER=логин_для_подключения
POSTGRES_PASSWORD=пароль_для_подключения_бд
POSTGRES_DB=имя_базы_данных
DB_HOST=название_сервиса
DB_PORT=порт_для_подключения_бд 
SECRET_KEY='ваш_секретный_ключ'
```

## Выполните команду

```
docker-compose up -d --build
```

## Выполните миграции
```
docker-compose exec backend python manage.py makemigrations recipes
docker-compose exec backend python manage.py makemigrations users
docker-compose exec backend python manage.py makemigrations 
docker-compose exec backend python manage.py migrate
```

## Создайте суперпользователя
```
docker-compose exec backend python manage.py createsuperuser
```
## Соберите статику
```
docker-compose exec backend python manage.py collectstatic --no-input
```

## Заполните базу тестовыми данными:
``` 
docker-compose exec backend python manage.py add_ingredients
```
## Адрес, где развернут проект
```
Адрес: http://checkfoodgram.ddns.net:8080/

```
