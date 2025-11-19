from django.contrib import admin
from django.db.models import Count
from .models import Ingredient, MeasurementUnit, Recipe, RecipeIngredient, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1
    fields = ['ingredient', 'amount']
    autocomplete_fields = ['ingredient']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'cooking_time',
        'get_favorite_count', 'get_tags',)
    list_filter = ('tags', 'author')
    search_fields = ('name', 'author__username', 'author__email')
    filter_horizontal = ('tags',)
    readonly_fields = ('get_favorite_count',)
    inlines = [RecipeIngredientInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'author', 'text', 'cooking_time', 'image')
        }),
        ('Теги', {
            'fields': ('tags',)
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            favorite_count=Count('in_favorites')
        ).prefetch_related('tags')

    def get_favorite_count(self, obj):
        return obj.favorite_count
    get_favorite_count.short_description = 'В избранном'
    get_favorite_count.admin_order_field = 'favorite_count'

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Теги'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'abbrev')
    search_fields = ('name', 'abbrev')
    ordering = ('name',)
