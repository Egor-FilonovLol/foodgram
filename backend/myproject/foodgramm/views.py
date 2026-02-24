from rest_framework import viewsets
from .models import Tag, Ingridient
from .serializers import TagSerializer, IngridientSerializer, UserCreateSerializer, UserListSerializer,ChangeUserPasswordSerializer
from rest_framework.permissions import AllowAny
from rest_framework import filters
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from .pagination import UserPagination
from rest_framework.decorators import action

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)


  #  def post(self, request):
   #     serializer = UserCreateSerializer(data=request.data)
     #   if serializer.is_valid():
    #        serializer.save()
      #      return Response(serializer.data, status=status.HTTP_201_CREATED)
       # return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = UserPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserListSerializer

    @action(methods=['post'], detail=False)
    def set_password(self, request):
        serializer = ChangeUserPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def me(self, request):
        serializer = UserListSerializer(request.user)
        return Response(serializer.data)