SPACES_4 = ' ' * 4
EXT = 'magic'
INDEX_F = 'index'
OUTPUT_FOLDER = 'build'

BUILD_MODELS_NAME = 'models.py'
BUILD_SERIALIZERS_NAME = 'serializers.py'
BUILD_APIVIEWS_NAME = 'apiviews.py'
BUILD_APIURLS_NAME = 'apiurls.py'

DJANGO_IMPORT_MODELS = 'from django.db import models'
DJANGO_IMPORT_SERIALIZERS = """from rest_framework import serializers
from . import models"""
DJANGO_IMPORT_APIVIEWS = """from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *"""
DJANGO_IMPORT_APIURLS = """from django.urls import path
from . import apiviews"""

DJANGO_DEFINITION_MODEL = 'class %s(models.Model):'
DJANGO_DEFINITION_META_CLASS = 'class Meta:'
DJANGO_DEFINITION_SERIALIZER = 'class %s(serializers.ModelSerializer):'
DJANGO_DEFINITION_API_CLASS = 'class %sAPI(APIView):'
DJANGO_DEFINITION_API_GET_HANDLER = """def get(self, request):
        {model_name_lower}_objs = {model_name}.objects.all()
        serializer = {serializer}({model_name_lower}_objs, many=True)
        return Response(serializer.data)"""
DJANGO_DEFINITION_API_POST_HANDLER = """def post(self, request):
        serializer = {serializer}(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)"""
DJANGO_DEFINITION_APIURL_PATH = "path('{model_kabab}', apiviews.{model}API.as_view()),"
DJANGO_SET_SERIALIZERS_MODEL = 'model = models.%s'
