from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from backend.settings import DNS_SERVER_NAME
from interaction.models import Favorites, Followers, ShoppingCart
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from users.serializers import (RecipeShortSerializer, UserAvatarSerializer,
                               UserSerializer, UserSubscribeSerializer)

from .filters import RecipeFilter
from .mixins import UserRelationMixin
from .permissions import IsAuthenticatedForCreate, IsAuthorForEdit
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, TagSerializer)
from . import constants as const


User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    ''' Overwrite 'me'(Djoser) '''
    serializer = UserSerializer(request.user, context={'request': request})
    return Response(serializer.data)


class SubscriptionsList(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(followers__user=self.request.user)

    def get_serializer_class(self):
        return UserSubscribeSerializer


class Subscribe(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSubscribeSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        ''' GET /api/users/{pk}/subscribe/ '''
        author = get_object_or_404(User, pk=self.kwargs['pk'])
        user = request.user
        if self.request.user == author:
            raise serializers.ValidationError(
                {"error": const.SUBSCRIBE_SELF_ADDING_ERROR})
        _, created = Followers.objects.get_or_create(user=user, author=author)
        if created:
            serializer = UserSubscribeSerializer(author,
                                                 context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": const.SUBSCRIBE_ALREADY_ERROR},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        ''' DELETE /api/users/{pk}/subscribe/ '''
        author = get_object_or_404(User, pk=self.kwargs['pk'])
        deleted, _ = Followers.objects.filter(
            user=request.user, author=author).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": "Subscription not found"},
                status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(UserRelationMixin, viewsets.ModelViewSet):
    ''' ViewSet for Users'''
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['PUT', 'DELETE'], url_path='me/avatar')
    def me_avatar(self, request):
        ''' Add endpoint /api/users/me/avatar
        Inplements HTTP PUT/DELETE methods '''
        if not request.user.is_authenticated:
            return Response(
                {"detail": const.USER_UNAUTHORIZED_ERROR},
                status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        if request.method == 'PUT':
            serializer = UserAvatarSerializer(user, data=request.data,
                                              partial=True,
                                              context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class RecipesViewSet(UserRelationMixin, viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    permission_classes = [IsAuthenticatedForCreate, IsAuthorForEdit]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_link(self, request, pk=None):
        ''' Add endpoint api/recipes/{pk}/get-link/
        Inplements HTTP POST/DELETE methods '''
        recipe = self.get_object()
        return Response({
            "short-link": recipe.short_link})

    @action(detail=True, methods=['POST', 'DELETE'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        ''' Add endpoint api/recipes/{pk}/shopping_cart/
        Inplements HTTP POST/DELETE methods '''
        recipe = self.get_object()
        user = request.user
        if request.method == 'POST':
            obj, created = ShoppingCart.objects.get_or_create(recipe=recipe,
                                                              user=user)
            if created:
                serializer = RecipeShortSerializer(recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'error': const.SHOPPING_CART_ADDING_ERROR},
                            status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            deleted, _ = ShoppingCart.objects.filter(recipe=recipe,
                                                     user=user).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': const.SHOPPING_CART_EMPTY_ERROR},
                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(
            user=user).select_related('recipe')
        if not shopping_cart.exists():
            return Response(
                {'error': const.SHOPPING_LIST_EMPTY_ERROR},
                status=status.HTTP_400_BAD_REQUEST)
        ingredients_dict = {}
        for item in shopping_cart:
            recipe = item.recipe
            for ingredient_amount in recipe.ingredient_amounts.all():
                ingredient = ingredient_amount.ingredient
                key = (ingredient.id, ingredient.name,
                       ingredient.measurement_unit.name)
                if key in ingredients_dict:
                    ingredients_dict[key] += ingredient_amount.amount
                else:
                    ingredients_dict[key] = ingredient_amount.amount
        content = f"{const.SHOPPING_LIST_TITLE}\n\n"
        content += f"{const.SHOPPING_LIST_SEPARATOR}\n\n"
        for i, ((ingredient_id, name, unit), amount) in enumerate(
                ingredients_dict.items(), 1):
            content += f"{i}. {name} - {amount} {unit}\n"
        content += f"\n{const.SHOPPING_LIST_SEPARATOR}\n"
        content += const.SHOPPING_LIST_TOTAL_ITEMS.format(
            count=len(ingredients_dict)) + "\n"
        content += const.SHOPPING_LIST_TOTAL_RECIPES.format(
            count=shopping_cart.count()) + "\n"
        response = HttpResponse(
            content, content_type=const.SHOPPING_LIST_CONTENT_TYPE)
        response['Content-Disposition'] = (
            f'attachment; filename="{const.SHOPPING_LIST_FILENAME}"')
        return response

    @action(detail=True, methods=['POST', 'DELETE'], url_path='favorite')
    def favorite(self, request, pk=None):
        ''' Add endpoint /api/recipes/{pk}/favotire/ '''
        recipe = self.get_object()
        user = request.user
        if request.method == 'POST':
            obj, created = Favorites.objects.get_or_create(recipe=recipe,
                                                           user=user)
            if created:
                serializer = RecipeShortSerializer(recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(
                {'error': const.FAVORITE_ADDING_ERROR},
                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            deleted, _ = Favorites.objects.filter(recipe=recipe,
                                                  user=user).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': const.FAVORITE_EMPTY_ERROR},
                status=status.HTTP_400_BAD_REQUEST)


class IngredientReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    permission_classes = [AllowAny]


class RecipeByShortId(RetrieveAPIView):
    ''' Get recipe by short_id '''
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = [AllowAny]
    lookup_field = 'short_id'
    lookup_url_kwarg = 'short_id'

    def get(self, request, *args, **kwargs):
        recipe = self.get_object()
        return redirect(f'http://{DNS_SERVER_NAME}:8000/recipes/{recipe.id}/')
