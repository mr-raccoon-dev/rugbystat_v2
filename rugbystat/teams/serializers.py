from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import ValidationError

from clippings.serializers import DocumentSerializer
from .models import Team, TeamSeason, City, Person, PersonSeason

__author__ = 'krnr'


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.__class__(value, context=self.context)
        return serializer.data


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    documents = DocumentSerializer(many=True)
    city = CitySerializer()
    parent = RecursiveField()

    class Meta:
        model = Team
        fields = ('url', 'id', 'name', 'short_name', 'story', 'city',
                  'year', 'disband_year', 'operational_years',
                  'parent', 'documents')


class TeamSeasonSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = TeamSeason
        fields = ('id', 'name', 'year', 'team', 'season', 'story',
                  'place', 'played', 'wins', 'draws', 'losses', 'points', 'score')


class PersonSeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonSeason
        fields = ('id', '__str__', 'person', 'team', 'season',
                  'year', 'story', 'role')

    def validate(self, attrs):
        kwargs = {field: attrs[field]
                  for field in ['person', 'year', 'team', 'role']}
        if PersonSeason.objects.filter(**kwargs).exists():
            raise ValidationError('Violates unique_together condition')
        return attrs


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    seasons = PersonSeasonSerializer(many=True)

    class Meta:
        model = Person
        fields = ('url', 'id', '__str__', 'full_name', 'story',
                  'year_birth', 'dob', 'year_death', 'dod', 'living_years',
                  'seasons')
