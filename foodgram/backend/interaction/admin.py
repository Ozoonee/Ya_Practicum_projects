from django.contrib import admin
from . import models


admin.site.register(models.Followers)
admin.site.register(models.ShoppingCart)


@admin.register(models.Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe', 'get_recipe_author')
    list_filter = ('user', 'recipe')
    search_fields = ('user__email', 'user__username', 'recipe__name')

    def get_recipe_author(self, obj):
        return obj.recipe.author
    get_recipe_author.short_description = 'Автор рецепта'
