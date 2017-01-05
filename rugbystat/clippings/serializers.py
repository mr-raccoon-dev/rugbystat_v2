from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, Serializer
from clippings.models import Document, Source, SourceObject

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
        fields = ('id', 'title', 'description', 'dropbox_path',
                  'dropbox_thumb', 'year', 'month', 'date', 'is_image',
                  'versions',
                  )


class SourceObjectSerializer(ModelSerializer):
    documents = DocumentSerializer(many=True)
    source = SerializerMethodField()

    class Meta:
        model = SourceObject
        fields = ('id', 'source', 'edition', 'year', 'date', 'documents')

    def get_source(self, obj):
        return obj.source.as_dict()


class SourceSerializer(ModelSerializer):
    documents = DocumentSerializer(many=True)
    instances = SourceObjectSerializer(many=True)

    class Meta:
        model = Source
        fields = ('title', 'type', 'instances', 'documents')

