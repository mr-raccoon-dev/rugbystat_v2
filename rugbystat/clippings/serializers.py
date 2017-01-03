from rest_framework.serializers import ModelSerializer
from clippings.models import Document

__author__ = 'krnr'


class DocumentSerializer(ModelSerializer):
    class Meta:
        model = Document
        fields = ('title', 'dropbox', 'dropbox_path', 'dropbox_thumb',
                  'year', 'month', 'date', 'is_image', 'versions')

    def get_fields(self):
        fields = super(DocumentSerializer, self).get_fields()
        fields['versions'] = DocumentSerializer(many=True)
        return fields
