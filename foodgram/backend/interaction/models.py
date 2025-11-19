from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class Favorites(models.Model):
    recipe = models.ForeignKey('recipes.Recipe',
                               on_delete=models.CASCADE,
                               related_name='in_favorites',
                               verbose_name=('Рецепт'))
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorite_recipes',
                             verbose_name='Автор')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ['user', 'recipe']

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class Followers(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='followers',
                               verbose_name='Автор')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='following',
                             verbose_name='Подписчик')

    def clean(self):
        if self.author == self.user:
            raise ValidationError('Нельзя подписываться на себя')

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписки'
        unique_together = ['author', 'user']
        constraints = [models.CheckConstraint(
            check=~models.Q(author=models.F('user')),
            name='prevent_self_following')]

    def __str__(self):
        return f"{self.user} - {self.author}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_cart',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey('recipes.Recipe',
                               on_delete=models.CASCADE,
                               related_name='in_shopping_cart',
                               verbose_name=('Рецепт'))

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        unique_together = ['user', 'recipe']

    def __str__(self):
        return f"{self.user} - {self.recipe}"
