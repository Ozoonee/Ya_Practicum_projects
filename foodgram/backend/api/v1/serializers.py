from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.utils import Base64ImageField
from interaction.models import Favorites, Followers, ShoppingCart
from recipes.constants import MAX_AMOUNT, MIN_AMOUNT
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.serializers import UserSerializer


User = get_user_model()


class FollowersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Followers
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField()

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit.name')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_AMOUNT,
        max_value=MAX_AMOUNT,
        error_messages={
            'min_value':
            f'Количество не может быть меньше {MIN_AMOUNT}',
            'max_value':
            f'Количество не может быть больше {MAX_AMOUNT}'})


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientReadSerializer(many=True,
                                                 source='ingredient_amounts')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorites.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        exclude = ['author']

    def validate(self, data):
        if 'ingredients' in data:
            if len(data['ingredients']) == 0:
                raise serializers.ValidationError({
                    'ingredients':
                      ['Список ингредиентов не может быть пустым']})

            ingredient_ids = [
                ingredient_data['id'].id for ingredient_data in data[
                    'ingredients']]
            if len(ingredient_ids) != len(set(ingredient_ids)):
                raise serializers.ValidationError({
                    'ingredients': ['Ингредиенты не должны повторяться']})
        if 'ingredients' not in data:
            raise serializers.ValidationError({
                'ingredients': ['Обязательное поле']})

        if 'tags' in data:
            if len(data['tags']) == 0:
                raise serializers.ValidationError({
                    'tags': ['Список тегов не может быть пустым.']})

            tag_ids = [tag.id for tag in data['tags']]
            if len(tag_ids) != len(set(tag_ids)):
                raise serializers.ValidationError({
                    'tags': ['Теги не должны повторяться']})
        if 'tags' not in data:
            raise serializers.ValidationError({
                'tags': ['Обязательное поле']})
        return data

    def create(self, validated_data):
        author = self.context['request'].user
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=author,
            **validated_data)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount'])
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            instance.tags.set(validated_data['tags'])
        if 'ingredients' in validated_data:
            instance.ingredient_amounts.all().delete()
            ingredients_data = validated_data['ingredients']
            for ingredient_data in ingredients_data:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient_data['id'],
                    amount=ingredient_data['amount'])
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        if 'image' in validated_data:
            instance.image = validated_data['image']
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data
