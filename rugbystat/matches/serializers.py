from rest_framework import serializers

from .models import Match


class MatchSerializer(serializers.ModelSerializer):
    name = serializers.CharField(default='default')
    
    class Meta:
        model = Match
        fields = (
            'name', 'story', 'date', 'tourn_season',
            'home', 'home_score', 'home_halfscore',
            'away', 'away_score', 'away_halfscore',
        )

    def validate_empty_values(self, data):
        flag, data = super().validate_empty_values(data)
        if data['story'] is None:
            data['story'] = ''
        return flag, data