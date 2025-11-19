from django_filters import rest_framework as filters
from interaction.models import ShoppingCart
from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        '''Favorite filter'''
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        '''Shopping cart filter'''
        if value and self.request and self.request.user.is_authenticated:
            cart_ids = ShoppingCart.objects.filter(
                user=self.request.user
            ).values_list('recipe_id', flat=True)
            return queryset.filter(id__in=cart_ids)
        return queryset
