from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views as vw

router = DefaultRouter()
router.register('users', vw.UserViewSet, basename='users')
router.register('tags', vw.TagReadOnlyViewSet)
router.register('recipes', vw.RecipesViewSet, basename='recipe')
router.register('ingredients', vw.IngredientReadOnlyViewSet)

urlpatterns = [
    path('s/<str:short_id>/', vw.RecipeByShortId.as_view(),
         name='recipe-by-short-id'),
    path('api/users/subscriptions/', vw.SubscriptionsList.as_view(),
         name='subscriptions'),
    path('api/users/<int:pk>/subscribe/', vw.Subscribe.as_view(),
         name='subscribe'),
    path('api/users/me/', vw.me, name='users-me'),
    path('api/', include('djoser.urls')),
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
]
