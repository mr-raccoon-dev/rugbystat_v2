import logging
import typing as t

from babel.dates import format_date
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from teams.models import TagObject, Team, TeamSeason
# from teams.models import Stadium, Person

logger = logging.getLogger("rugbystat")


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

    def get_name_with_seasons(self):
        """Iterate on all related seasons to find first and last.

        E.g. Чемпионат СССР (1936-1991)"""
        all_seasons = list(self.seasons.all())
        try:
            first = all_seasons[0]
            last = all_seasons[-1]

            years = first.date_start.year
            if last.date_end.year != years:
                years = f'{years}-{last.date_end.year}'
        except IndexError:
            years = "-"

        return f'{self.name} ({years})'


class Season(TagObject):
    """Each specific drawing of a Tournament"""

    tourn = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, verbose_name=_("Турнир"), related_name="seasons"
    )
    date_start = models.DateField(verbose_name=_("Дата начала"))
    date_end = models.DateField(verbose_name=_("Дата окончания"))

    participants = models.PositiveSmallIntegerField(
        verbose_name=_('Число участников'), blank=True, null=True,
    )

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
    """Stage of a Season: preliminary round, group A/gmroup B, etc."""

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
        Season, on_delete=models.CASCADE, verbose_name=_("Розыгрыш"), related_name="groups",
    )
    round_type = models.CharField(
        verbose_name=_("Тип игр"), max_length=127, choices=TYPES, default=ROUND,
    )
    date_start = models.DateField(verbose_name=_("Дата начала"))
    date_end = models.DateField(verbose_name=_("Дата окончания"))
    city = models.ForeignKey(
        "teams.City", on_delete=models.CASCADE, 
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
        return qs.order_by('date', 'pk')

    def fill_blanks(self):
        for gs in self.standings.all():
            try:
                gs.build().save()
            except ValueError as exc:
                logger.warning(f"{gs} matches: {exc}")


class MatchQuerySet(models.QuerySet):
    def for_team(self, team_pk):
        return self.filter(models.Q(home_id=team_pk) | models.Q(away_id=team_pk))


class Match(TagObject):

    _delimiter = '—'

    date = models.DateField(verbose_name="Дата матча", blank=True, null=True)
    date_unknown = models.CharField(
        verbose_name="Дата, если неизвестна",
        max_length=64, blank=True, null=True,
    )
    display_name = models.CharField(verbose_name="Отображение", max_length=255, blank=True)
    tourn_season = models.ForeignKey(
        Season, on_delete=models.SET_NULL,
        verbose_name=_("Турнир"), related_name="matches", blank=True, null=True
    )
    home = models.ForeignKey(
        Team, on_delete=models.CASCADE,
        verbose_name=_("Хозяева"), related_name="home_matches"
    )
    away = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name=_("Гости"), related_name="away_matches")
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

    # в случае потасовки на поле возможно поражение ОБЕИМ командам
    technical = models.BooleanField(verbose_name=_("Технический результат"), default=False)
    tech_home_loss = models.BooleanField(verbose_name=_("Поражение хозяевам"), default=False)
    tech_away_loss = models.BooleanField(verbose_name=_("Поражение гостям"), default=False)

    objects = MatchQuerySet.as_manager()

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.display_name:
            self.update_match_name()
        super(Match, self).save(**kwargs)

    @property
    def is_unknown_outcome(self):
        return "??:??" in self.name

    @property
    def is_only_outcome(self):
        return any([self.tech_away_loss, self.tech_home_loss])

    @property
    def is_unknown_score(self):
        if self.is_unknown_outcome:
            return True

        for unkn in ("в:п", "п:в", "н:н"):
            if unkn in self.name:
                return True
        return False

    @property
    def is_home_win(self):
        if self.is_only_outcome:
            return self.tech_away_loss
        if not self.is_unknown_outcome:
            return self.home_score > self.away_score

    @property
    def is_away_win(self):
        if self.is_only_outcome:
            return self.tech_home_loss
        if not self.is_unknown_outcome:
            return self.home_score < self.away_score

    @property
    def is_draw(self):
        if not self.is_unknown_outcome:
            return not self.is_only_outcome and self.home_score == self.away_score

    def is_team_win(self, team_id):
        if team_id == self.home_id:
            return self.is_home_win
        if team_id == self.away_id:
            return self.is_away_win

    def is_team_loss(self, team_id):
        if team_id == self.home_id:
            return self.is_away_win
        if team_id == self.away_id:
            return self.is_home_win

    def team_score(self, team_id):
        if team_id == self.home_id:
            return self.home_score, self.away_score
        if team_id == self.away_id:
            return self.away_score, self.home_score

    def set_tech_score(self):
        if self.home_score == "-":
            self.technical = True
            self.home_score = None
            self.tech_home_loss = True
        if self.home_score == "+":
            self.technical = True
            self.home_score = None
            self.tech_away_loss = True
        if self.away_score == "-":
            self.technical = True
            self.away_score = None
            self.tech_away_loss = True
        if self.away_score == "+":
            self.technical = True
            self.away_score = None
            self.tech_home_loss = True

    def _get_name_for_tournament(self, team_id) -> t.Optional[str]:
        team_season = self.tourn_season.standings.filter(team_id=team_id).first()
        if team_season:
            return team_season.name
        return ''

    def _get_names_for_date(self):
        """Return teams names for a match date"""
        home = self._get_name_for_tournament(self.home_id)
        away = self._get_name_for_tournament(self.away_id)
        undefined = not home or not away
        if undefined and self.date:
            home = self.home.get_name_for(self.date.year, self.date.month, self.date.day)
            away = self.away.get_name_for(self.date.year, self.date.month, self.date.day)
        return home, away

    def _get_score(self):
        if self.technical:
            home_score = "+" if self.tech_away_loss else "-"
            away_score = "+" if self.tech_home_loss else "-"
        elif self.tech_home_loss:
            home_score, away_score = "п", "в"
        elif self.tech_away_loss:
            home_score, away_score = "в", "п"
        else:
            home_score = "??" if self.home_score is None else self.home_score
            away_score = "??" if self.away_score is None else self.away_score

        # TODO: deal with draws without putting 1s into score!
        if home_score == 1 and away_score == 1:
            home_score, away_score = "н", "н"
        return home_score, away_score

    def _get_name_from_score(self, teams: t.Optional[t.Tuple[str, str]] = None):
        home_score, away_score = self._get_score()
        teams_names = teams or self._get_names_for_date()
        teams_names = f" {self._delimiter} ".join(teams_names)
        name = "{} {} {}:{}".format(teams_names, self._delimiter, home_score, away_score)

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

    def update_match_name(self):
        date = self.date_unknown
        if self.date and not date:
            date = self.date.strftime("%Y-%m-%d")

        self.display_name = self._get_name_from_score()
        self.name = "{} {}".format(date, self.display_name)
        return self

    def get_absolute_url(self):
        lap = self.tourn_season._get_lap().replace("/", "-")
        return reverse(
            "match_detail",
            kwargs={
                "tourn_pk": self.tourn_season.tourn_id,
                "lap": lap,
                "season_pk": self.tourn_season_id,
                "pk": self.pk,
            },
        )

    def get_display_with_links(self):
        home, away, score = self.display_name.split(self._delimiter)

        ts_qs = TeamSeason.objects.filter(
            season=self.tourn_season,
            team__in=[self.home, self.away]
        )
        ts_instances = {ts.team_id: ts for ts in ts_qs}

        home_link = ts_instances[self.home_id].get_absolute_url()
        away_link = ts_instances[self.away_id].get_absolute_url()
        h_href = f'<a href="{home_link}">{home.strip()}</a>'
        a_href = f'<a href="{away_link}">{away.strip()}</a>'
        return f" {self._delimiter} ".join([h_href, a_href, score.strip()])

    def get_date(self):
        """Unknown field always has priority."""
        if self.date_unknown:
            date = f"{self.date_unknown}."
        else:
            date = format_date(self.date, format='long', locale='ru').replace(' г.', '.')
        return date

    def swap(self):
        """Swap home<>away"""
        self.home, self.away = self.away, self.home
        self.home_score, self.away_score = self.away_score, self.home_score
        self.home_halfscore, self.away_halfscore = self.away_halfscore, self.home_halfscore
        self.tech_home_loss, self.tech_away_loss = self.tech_away_loss, self.tech_home_loss
        self.save()
