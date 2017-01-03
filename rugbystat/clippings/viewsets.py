from rest_framework import viewsets


from .models import Document
from .serializers import DocumentSerializer

__author__ = 'krnr'


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
