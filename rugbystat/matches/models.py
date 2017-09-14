from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
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
    level = models.PositiveSmallIntegerField(
        verbose_name=_('Уровень'), default=0, blank=False, null=False
    )

    class Meta:
        ordering = ('level', )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tournament_detail', kwargs={'pk': self.pk})


class Season(TagObject):
    """Each specific drawing of a Tournament"""
    tourn = models.ForeignKey(
        Tournament, verbose_name=_("Турнир"), related_name='seasons')
    date_start = models.DateField(verbose_name=_("Дата начала"))
    date_end = models.DateField(verbose_name=_("Дата окончания"))

    class Meta:
        ordering = ('tourn', 'date_start')

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        self.full_clean()
        if not self.pk:
            self.name = self._get_name()
        super(Season, self).save(**kwargs)

    def full_clean(self, **kwargs):
        super(Season, self).full_clean(**kwargs)
        name = self._get_name()
        if Season.objects.filter(name=name).exclude(pk=self.pk).exists():
            msg = 'Such season already exists: {}'
            raise ValidationError(msg.format(name))

    def get_absolute_url(self):
        lap = self._get_lap().replace('/', '-')
        return reverse('season_detail',
                       kwargs={
                           'tourn_pk': self.tourn_id,
                           'lap': lap,
                           'pk': self.pk,
                       })

    def get_table(self):
        """
        Return list of TeamSeason-s sorted by place
        """
        return self.standings.order_by('order')

    def _get_lap(self):
        """
        Return year part for season: '1977' for Чемпионат СССР 1978
        '1977/78' for Кубок СССР 1977/78
        """
        if self.date_start.year == self.date_end.year:
            lap = str(self.date_start.year)
        else:
            lap = "{}/{}".format(
                self.date_start.year, str(self.date_end.year)[-2:])
        return lap

    def _get_name(self):
        """
        Generate name like Чемпионат СССР 1978 or Кубок СССР 1977/78
        """
        return "{} {}".format(self.tourn, self._get_lap())


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
