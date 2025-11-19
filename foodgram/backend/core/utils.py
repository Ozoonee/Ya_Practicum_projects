import base64
import re
import time
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            filename = f"image_{int(time.time())}_{uuid.uuid4().hex[:8]}.{ext}"
            data = ContentFile(base64.b64decode(imgstr), name=filename)
        return super().to_internal_value(data)


def has_cyrillic(text):
    """Cyrillic alphabet verification"""
    return bool(re.search('[а-яА-ЯёЁ]', text))
