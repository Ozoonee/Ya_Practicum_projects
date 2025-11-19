import re

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from . import constants as const


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=const.MAX_LENGTH_FIRST_NAME,
                                  blank=False, null=False)
    last_name = models.CharField(max_length=const.MAX_LENGTH_LAST_NAME,
                                 blank=False, null=False)
    email = models.EmailField(max_length=const.MAX_LENGTH_EMAIL,
                              unique=True,
                              blank=False, null=False)
    avatar = models.ImageField(upload_to='users_avatar/',
                               blank=True,
                               null=True,
                               verbose_name='Аватар пользователя')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def clean(self):
        super().clean()
        if self.username:
            if not re.match(r'^[\w.@+-]+\Z', self.username):
                raise ValidationError({
                    'username': 'Имя пользователя может содержать '
                    'только буквы, цифры и символы @/./+/-/_'})
