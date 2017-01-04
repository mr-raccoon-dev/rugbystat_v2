from django.db import models
from django.utils.translation import ugettext_lazy as _

from teams.models import TagObject, Team, Stadium, Person


class Tournament(TagObject):
    pass


class Season(TagObject):
    tourn = models.ForeignKey(
        Tournament, verbose_name="Турнир", related_name='seasons')


class Match(TagObject):
    home = models.ForeignKey(
        Team, verbose_name=_("Хозяева"), related_name='home_matches', )
    away = models.ForeignKey(
        Team, verbose_name=_("Гости"), related_name='away_matches', )
    home_score = models.PositiveSmallIntegerField(
        verbose_name=_("Счёт хозяев"), blank=True, null=True, )
    away_score = models.PositiveSmallIntegerField(
        verbose_name=_("Счёт гостей"), blank=True, null=True, )
    date = models.DateField(
        verbose_name="Дата матча", blank=True, null=True, )

    tourn_season = models.ForeignKey(
        Season, verbose_name=_("Турнир"), related_name='matches',
        blank=True, null=True)
    stadium = models.ForeignKey(
        Stadium, verbose_name=_("Стадион"), related_name='matches',
        blank=True, null=True)
    ref = models.ForeignKey(
        Person, verbose_name=_("Судья"), related_name='matches_reffed',
        blank=True, null=True)
