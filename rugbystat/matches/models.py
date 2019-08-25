from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from teams.models import TagObject, Team
# from teams.models import Stadium, Person


class Tournament(TagObject):
    """Representation of each tournament that might exist:

    - Чемпионат СССР
    - Чемпионат СССР. Первая лига
    - Кубок СССР
    - Первенство Украины
    ...
    """

    level = models.PositiveSmallIntegerField(
        verbose_name=_("Уровень"), default=0, blank=False, null=False
    )

    class Meta:
        ordering = ("level",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tournament_detail", kwargs={"pk": self.pk})


class Season(TagObject):
    """Each specific drawing of a Tournament"""

    tourn = models.ForeignKey(
        Tournament, verbose_name=_("Турнир"), related_name="seasons"
    )
    date_start = models.DateField(verbose_name=_("Дата начала"))
    date_end = models.DateField(verbose_name=_("Дата окончания"))

    class Meta:
        ordering = ("tourn", "date_start")

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
            msg = "Such season already exists: {}"
            raise ValidationError(msg.format(name))

    def get_absolute_url(self):
        lap = self._get_lap().replace("/", "-")
        return reverse(
            "season_detail",
            kwargs={"tourn_pk": self.tourn_id, "lap": lap, "pk": self.pk},
        )

    def get_table(self):
        """
        Return list of TeamSeason-s sorted by place
        """
        return self.standings.order_by("order")

    def _get_lap(self):
        """
        Return year part for season: '1977' for Чемпионат СССР 1978
        '1977/78' for Кубок СССР 1977/78
        """
        if self.date_start.year == self.date_end.year:
            lap = str(self.date_start.year)
        else:
            lap = "{}/{}".format(self.date_start.year, str(self.date_end.year)[-2:])
        return lap

    def _get_name(self):
        """
        Generate name like Чемпионат СССР 1978 or Кубок СССР 1977/78
        """
        return "{} {}".format(self.tourn, self._get_lap())


class Group(models.Model):
    """Stage of a Season: preliminary round, group A/group B, etc."""

    ROUND = 'round-robin'
    KNOCKOUT = 'knockout'
    MISC = 'misc'
    TYPES = (
        (ROUND, ROUND),
        (KNOCKOUT, KNOCKOUT),
        (MISC, MISC)
    )

    name = models.CharField(verbose_name=_("Название"), max_length=127, blank=True)
    season = models.ForeignKey(
        Season, verbose_name=_("Розыгрыш"), related_name="groups",
    )
    round_type = models.CharField(
        verbose_name=_("Тип игр"), max_length=127, choices=TYPES, default=ROUND,
    )
    date_start = models.DateField(verbose_name=_("Дата начала"))
    date_end = models.DateField(verbose_name=_("Дата окончания"))
    city = models.ForeignKey(
        "teams.City",
        verbose_name=_("Город"),
        related_name="groups",
        blank=True,
        null=True,
    )
    comment = models.TextField(verbose_name=_("Комментарий"), blank=True)
    teams = models.ManyToManyField(
        "teams.TeamSeason", related_name="groups", blank=True
    )

    class Meta:
        ordering = ("season", "date_end")

    def __str__(self):
        return "{0.date_start.year} {0.name}".format(self)

    def get_table(self):
        """
        Return list of GroupSeason-s sorted by place
        """
        return self.standings.order_by("order")

    @property
    def is_round_robin(self):
        return self.round_type == self.ROUND

    def matches(self):
        """Return all matches of the season which belong to the group."""
        teams = self.teams.values_list('team', flat=True)
        qs = self.season.matches.filter(home__in=teams, away__in=teams)
        qs = qs.exclude(date__lt=self.date_start)
        qs = qs.exclude(date__gt=self.date_end)
        return qs


class Match(TagObject):
    date = models.DateField(verbose_name="Дата матча", blank=True, null=True)
    tourn_season = models.ForeignKey(
        Season, verbose_name=_("Турнир"), related_name="matches", blank=True, null=True
    )
    home = models.ForeignKey(
        Team, verbose_name=_("Хозяева"), related_name="home_matches"
    )
    away = models.ForeignKey(Team, verbose_name=_("Гости"), related_name="away_matches")
    home_score = models.PositiveSmallIntegerField(
        verbose_name=_("Счёт хозяев"), blank=True, null=True
    )
    away_score = models.PositiveSmallIntegerField(
        verbose_name=_("Счёт гостей"), blank=True, null=True
    )
    home_halfscore = models.PositiveSmallIntegerField(
        verbose_name=_("1 тайм хозяев"), blank=True, null=True
    )
    away_halfscore = models.PositiveSmallIntegerField(
        verbose_name=_("1 тайм гостей"), blank=True, null=True
    )

    def __str__(self):
        return self._get_name_from_score()

    def _get_name_from_score(self):
        home_score = "??" if self.home_score is None else self.home_score
        away_score = "??" if self.away_score is None else self.away_score

        if home_score == 1:
            home_score = "в"
            away_score = "п"
        if away_score == 1:
            away_score = "в"
            home_score = "п"

        name = "{} - {} - {}:{}".format(
            self.home.short_name, self.away.short_name, home_score, away_score
        )

        # add halftime
        home_halfscore = (
            "??" if self.home_halfscore is None else self.home_halfscore
        )  # noqa
        away_halfscore = (
            "??" if self.away_halfscore is None else self.away_halfscore
        )  # noqa
        if any((self.home_halfscore is not None, self.away_halfscore is not None)):
            name = "{} ({}:{})".format(name, home_halfscore, away_halfscore)

        return name

    def save(self, **kwargs):
        if not self.pk:
            self.name = self._get_name_from_score()
        super(Match, self).save(**kwargs)

    def get_absolute_url(self):
        # TODO
        return ""
