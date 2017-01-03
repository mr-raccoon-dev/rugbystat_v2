from rest_framework import viewsets, filters


from .models import Document
from .serializers import DocumentSerializer

__author__ = 'krnr'


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('year', 'date', 'is_image')
