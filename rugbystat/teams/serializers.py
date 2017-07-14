from rest_framework import serializers

from clippings.serializers import DocumentSerializer
from .models import Team, City, Person, PersonSeason

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


class PersonSeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonSeason
        fields = ('id', '__str__', 'person', 'team', 
                  'year', 'story', 'role')


class PersonSerializer(serializers.ModelSerializer):
    seasons = PersonSeasonSerializer(many=True)

    class Meta:
        model = Person
        fields = ('id', '__str__', 'full_name', 'story',
                  'year', 'dob', 'year_death', 'dod', 'living_years',
                  'seasons')

