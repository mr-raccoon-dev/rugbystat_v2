from django.db import models
from django.utils.translation import ugettext_lazy as _

from teams.models import TagObject, Team, Stadium, Person


class Tournament(TagObject):
    """Representation of each tournament that might exist:

    - Чемпионат СССР
    - Чемпионат СССР. Первая лига
    - Кубок СССР
    - Первенство Украины
    ...
    """
    # TODO: might have some `level` field
    def __str__(self):
        return self.name


class Season(TagObject):
    """Each specific drawing of a Tournament"""
    tourn = models.ForeignKey(
        Tournament, verbose_name=_("Турнир"), related_name='seasons')
    date_start = models.DateField(verbose_name=_("Дата начала"))
    date_end = models.DateField(verbose_name=_("Дата окончания"))

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.pk:
            if self.date_start.year == self.date_end.year:
                lap = self.date_start.year
            else:
                lap = "{}/{}".format(
                    self.date_start.year, str(self.date_end.year)[-2:])
            self.name = "{} {}".format(self.tourn, lap)
        super(Season, self).save(**kwargs)


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

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.pk:
            home_score = self.home_score or '??'
            away_score = self.away_score or '??'

            if home_score == 1:
                home_score = "+"
            if away_score == 1:
                away_score = "+"

            self.name = "{} - {} - {}:{}".format(
                self.home, self.away, home_score, away_score, )
        super(Match, self).save(**kwargs)
