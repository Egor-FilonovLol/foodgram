from rest_framework import routers
from django.urls import include, path
from .views import TagViewSet, IngridientViewSet, UserViewset


router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngridientViewSet, basename='ingredients')
router.register('users', UserViewset, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
