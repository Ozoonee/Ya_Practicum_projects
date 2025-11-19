from core.utils import Base64ImageField
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from interaction.models import Followers
from recipes.models import Recipe
from rest_framework import serializers

User = get_user_model()


class UserCreationSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name', 'email', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        ''' Сhecks the user is subscribed to the author of the request '''
        request = self.context.get('request')
        if (request and request.user.is_authenticated and not
                request.user.is_anonymous):
            return Followers.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance

    def validate(self, attrs):
        if 'avatar' not in attrs or not attrs['avatar']:
            raise serializers.ValidationError({"avatar": "Обязательное поле"})
        return attrs


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_count', 'avatar')

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit_str = request.query_params.get(
            'recipes_limit') if request else None
        if limit_str:
            limit = int(limit_str)
            recipes = obj.recipes.all()[:limit]
            return RecipeShortSerializer(recipes, many=True).data
        return RecipeShortSerializer(obj.recipes.all(), many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
