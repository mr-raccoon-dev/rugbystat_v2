from rest_framework.serializers import ModelSerializer, Serializer
from clippings.models import Document

__author__ = 'krnr'


class DocumentSubSerializer(ModelSerializer):
    class Meta:
        model = Document
        fields = ('title', 'dropbox_path', 'dropbox_thumb',
                  'year', 'month', 'date', 'is_image',
                  )


# class RecursiveField(Serializer):
#     def to_representation(self, value):
#         serializer = self.parent.parent.__class__(value, context=self.context)
#         serializer.data.pop('versions')  # serializer.data may raise RecursiveError
#         return serializer.data


class DocumentSerializer(ModelSerializer):
    versions = DocumentSubSerializer(many=True)
    # versions = RecursiveField(many=True)
    class Meta:
        model = Document
        fields = ('title', 'description', 'dropbox_path', 'dropbox_thumb',
                  'year', 'month', 'date', 'is_image',
                  'versions'
                  )
