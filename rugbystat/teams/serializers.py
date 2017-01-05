from rest_framework import serializers

from clippings.serializers import DocumentSerializer
from .models import Team, City

__author__ = 'krnr'


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.__class__(value, context=self.context)
        return serializer.data


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True)
    city = CitySerializer()
    parent = RecursiveField()

    class Meta:
        model = Team
        fields = ('id', 'name', 'short_name', 'story', 'city',
                  'year', 'disband_year', 'operational_years',
                  'parent', 'documents')
