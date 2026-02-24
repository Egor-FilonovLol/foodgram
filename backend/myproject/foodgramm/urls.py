from rest_framework import routers
from django.urls import include, path
from .views import TagViewSet


router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')


urlpatterns = [
    path('', include(router.urls))
]
