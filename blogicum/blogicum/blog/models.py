from django.db import models
from django.contrib.auth import get_user_model
from constants import MAX_TITLE_LEN, MAX_NAME_LEN


User = get_user_model()


class AbstractBaseModel(models.Model):
    is_published = models.BooleanField(default=True,
                                       verbose_name='Опубликовано',
                                       help_text=('Снимите галочку, чтобы'
                                                  ' скрыть публикацию.'))
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Добавлено')

    class Meta:
        abstract = True


class Category(AbstractBaseModel):
    title = models.CharField(max_length=MAX_TITLE_LEN,
                             verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены символы латиницы,'
            ' цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Location(AbstractBaseModel):
    name = models.CharField(max_length=MAX_NAME_LEN,
                            verbose_name='Название места')

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Post(AbstractBaseModel):
    title = models.CharField(max_length=MAX_TITLE_LEN,
                             verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем — можно делать '
                   'отложенные публикации.'))
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор публикации')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL,
                                 null=True, blank=True,
                                 verbose_name='Местоположение')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, blank=False,
                                 verbose_name='Категория')
    image = models.ImageField('Изображение', upload_to='posts_images',
                              blank=True)
    comment_count = models.PositiveIntegerField(
        default=0, verbose_name='Количество комментариев', editable=False)

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"

    def __str__(self):
        return self.title


class Comment(AbstractBaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор комментария')
    post = models.ForeignKey(Post, verbose_name="Публикация",
                             related_name="comments",
                             on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Текст комментария')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author}/{self.post.id}'
