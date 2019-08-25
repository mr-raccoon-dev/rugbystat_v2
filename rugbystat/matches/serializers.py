from rest_framework import serializers

from .models import Match


class MatchSerializer(serializers.ModelSerializer):
    name = serializers.CharField(default='default')
    
    class Meta:
        model = Match
        fields = '__all__'
