import shortuuid
from core.utils import has_cyrillic
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from transliterate import translit

from .models import Recipe, Tag


@receiver(pre_save, sender=Tag)
def generate_tag_slug(sender, instance, **kwargs):
    """ Generate SLUG before save object """
    if not instance.slug:
        base_slug = (translit(instance.name, 'ru', reversed=True)
                     if has_cyrillic(instance.name)
                     else instance.name)
        base_slug = slugify(base_slug)
        if not sender.objects.filter(slug=base_slug
                                     ).exclude(pk=instance.pk).exists():
            instance.slug = base_slug


@receiver(pre_save, sender=Recipe)
def generate_short_id(sender, instance, **kwargs):
    """ Generate short is before save object """
    if not instance.short_id:
        instance.short_id = shortuuid.ShortUUID().random(length=5)
