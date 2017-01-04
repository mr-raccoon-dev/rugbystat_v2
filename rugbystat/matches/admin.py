from django.contrib import admin
from matches.models import Tournament, Season, Match


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    pass

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    pass

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    pass
