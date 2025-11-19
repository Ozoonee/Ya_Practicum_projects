from backend.settings import DNS_SERVER_NAME
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from . import constants as const

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(const.MIN_COOKING_TIME),
                    MaxValueValidator(const.MAX_COOKING_TIME)],
        verbose_name='Время приготовления')
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField('Ingredient',
                                         through='RecipeIngredient',
                                         related_name='recipes',
                                         verbose_name='Ингредиенты')
    name = models.CharField(max_length=const.MAX_LENGTH_NAME,
                            verbose_name='Название')
    image = models.ImageField(upload_to='food_pictures/',
                              blank=True,
                              verbose_name='Изображение')
    short_id = models.CharField(max_length=10,
                                unique=True,
                                blank=True,
                                verbose_name='Короткий ID')
    tags = models.ManyToManyField('Tag',
                                  related_name='recipes',
                                  verbose_name='Тег')

    @property
    def short_link(self):
        return f"http://{DNS_SERVER_NAME}:8000/s/{self.short_id}/"

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=const.MAX_LENGTH_TAG_NAME,
                            unique=True,
                            verbose_name='Название')
    slug = models.SlugField(max_length=const.MAX_LENGTH_SLUG,
                            unique=True,
                            blank=True,
                            verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class MeasurementUnit(models.Model):
    name = models.CharField(max_length=const.MAX_LENGTH_UNIT,
                            unique=True,
                            verbose_name='Ед. измерения')
    abbrev = models.CharField(max_length=const.MAX_LENGTH_ABBREV,
                              unique=True,
                              verbose_name='Сокращение')

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=const.MAX_LENGTH_INGREDIENT_NAME,
                            unique=True,
                            verbose_name='Ингредиент')
    measurement_unit = models.ForeignKey(MeasurementUnit,
                                         on_delete=models.PROTECT,
                                         verbose_name='Ед. измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='ingredient_amounts')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='recipe_amounts')
    amount = models.SmallIntegerField(
        validators=[MinValueValidator(const.MIN_AMOUNT),
                    MaxValueValidator(const.MAX_AMOUNT)],
        verbose_name='Количество')

    class Meta:
        unique_together = ['recipe', 'ingredient']
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return f"{self.ingredient} - {self.amount}"
