from rest_framework import viewsets
from .models import Tag, Ingridient
from .serializers import TagSerializer, IngridientSerializer, UserCreateSerializer, UserListSerializer,ChangeUserPasswordSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import filters
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from .pagination import UserPagination
from rest_framework.decorators import action
from .serializers import AvatarSerializer
User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    filter_backends = [filters.SearchFilter]
    permission_classes = (AllowAny,)
    search_fields = ('name',)


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = UserPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserListSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(methods=['post'], detail=False)
    def set_password(self, request):
        serializer = ChangeUserPasswordSerializer(data=request.data,
                                                  context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def me(self, request):
        serializer = UserListSerializer(request.user,
                                        context={'request': request})
        return Response(serializer.data)

    @action(methods=['put', 'delete'], detail=False, url_path='me/avatar')
    def me_avatar(self, request):
        # нужно возвращать
        if request.method == 'PUT':
            serializer = AvatarSerializer(instance=request.user,
                                          data=request.data,
                                          partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if request.user.avatar:
                avatar_url = request.build_absolute_uri(request.user.avatar.url)
                return Response({'avatar': avatar_url}, status=status.HTTP_200_OK)
            return Response({'avatar': None}, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            if request.user.avatar:
                request.user.avatar.delete(save=False)
            request.user.avatar = None
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST'], detail=False, url_path='auth/token/logout')
    def logout(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
