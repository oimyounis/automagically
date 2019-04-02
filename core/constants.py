SPACES_4 = ' ' * 4
EXT = 'magic'
INDEX_F = 'index'
OUTPUT_FOLDER = 'build'

BUILD_MODELS_NAME = 'models.py'
BUILD_SERIALIZERS_NAME = 'serializers.py'

DJANGO_IMPORT_MODELS = 'from django.db import models'
DJANGO_IMPORT_SERIALIZERS = """from rest_framework import serializers
from . import models"""

DJANGO_DEFINITION_MODEL = 'class %s(models.Model):'
DJANGO_DEFINITION_META_CLASS = 'class Meta:'
DJANGO_DEFINITION_SERIALIZER = 'class %sSerializer(serializers.ModelSerializer):'
DJANGO_SET_SERIALIZERS_MODEL = 'model = models.%s'
