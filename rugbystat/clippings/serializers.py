from rest_framework.serializers import ModelSerializer
from clippings.models import Document

__author__ = 'krnr'


class DocumentSerializer(ModelSerializer):
    class Meta:
        model = Document
        fields = ('title', 'dropbox', 'dropbox_path', 'dropbox_thumb',
                  'year', 'month', 'date', 'is_image', 'versions')

DocumentSerializer.base_fields['versions'] = DocumentSerializer()
