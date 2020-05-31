import datetime as dt

from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from markdownx.models import MarkdownxField


class TagObject(models.Model):
    name = models.CharField(max_length=127, verbose_name=_('Базовое название'))
    story = MarkdownxField(verbose_name=_('История'), blank=True, )

    def __str__(self):
        return "Model: {0}".format(repr(self.target))

    @property
    def target(self):
        if getattr(self, 'team', None) is not None:
            return self.team
        if getattr(self, 'tournament', None) is not None:
            return self.tournament
        if getattr(self, 'season', None) is not None:
            return self.season
        if getattr(self, 'match', None) is not None:
            return self.match
        if getattr(self, 'person', None) is not None:
            return self.person
        return None

    @cached_property
    def documents(self):
        """
        >>> person.tagobject_ptr.document_set.all()
        <QuerySet [<Document: 1933>]>

        :return:
        :rtype:
        """
        return self.tagobject_ptr.document_set.all()


class TagThrough(models.Model):
    document = models.ForeignKey('clippings.Document')
    tag = models.ForeignKey('TagObject')


class City(models.Model):
    name = models.CharField(max_length=127, verbose_name=_('Базовое название'))
    short_name = models.CharField(
        max_length=4, verbose_name=_('Короткое название'), blank=True)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name

    def get_short_name(self):
        return self.short_name or self.name


class Stadium(models.Model):
    city = models.ForeignKey(City, verbose_name=_('Город'))
    name = models.CharField(max_length=127, verbose_name=_('Базовое название'))
    # TODO add historic names

    def __str__(self):
        return self.name


class Team(TagObject):
    CLUB = 'club'
    YOUTH = 'youth'
    NATION = 'nation'
    FOREIGN = 'foreign'
    TYPES = (
        (CLUB, CLUB),
        (YOUTH, YOUTH),
        (NATION, NATION),
        (FOREIGN, FOREIGN),
    )
    team_type = models.CharField(
        max_length=32, verbose_name=_('Короткое название'), choices=TYPES, default=CLUB,
    )
    short_name = models.CharField(
        max_length=32, verbose_name=_('Короткое название'), blank=True)
    city = models.ForeignKey(
        City, verbose_name=_('Город'), related_name='teams')
    year = models.PositiveSmallIntegerField(
        verbose_name=_('Год создания'), blank=True, null=True,
        validators=(MinValueValidator(1900), MaxValueValidator(2100)),
    )
    disband_year = models.PositiveSmallIntegerField(
        verbose_name=_('Год распада'), blank=True, null=True,
        validators=(MinValueValidator(1900), MaxValueValidator(2100)),
    )
    year_prefix = models.CharField(
        max_length=64, verbose_name=_('Префикс к году образования'),
        blank=True, null=True,)
    disband_year_prefix = models.CharField(
        max_length=64, verbose_name=_('Префикс к году распада'),
        blank=True, null=True,)
    parent = models.ForeignKey(
        'self', verbose_name=_('Команда-родитель'),
        related_name='ancestors', blank=True, null=True)

    class Meta:
        ordering = ('year', )

    def __str__(self):
        team = self.short_name or self.name
        return "{} ({})".format(team, self.operational_years)

    def save(self, **kwargs):
        if not self.short_name:
            self.short_name = "{} {}".format(self.name,
                                             self.city.get_short_name())
        super(Team, self).save(**kwargs)

    @cached_property
    def operational_years(self):
        years = "{}{}".format(self.year_prefix or '',
                              self.year or '')
        if self.disband_year or self.disband_year_prefix:
            years += "-{}{}".format(self.disband_year_prefix or '',
                                    self.disband_year or '')
        return years

    def get_absolute_url(self):
        return reverse('teams_detail', kwargs={'pk': self.pk})

    def get_name_for(self, year, month=1, day=1):
        """Return name which team born in a given year."""
        default = self.short_name
        from_db = self.names.reverse().filter(
            from_day__lte=dt.date(year, month, day)
        ).values_list('name', flat=True).first()
        return from_db or default


class TeamName(models.Model):
    """Representation of a separate name a team beared."""

    name = models.CharField(verbose_name=_('Базовое название'), max_length=127)
    team = models.ForeignKey(Team, verbose_name=_('Команда'), related_name='names')
    from_day = models.DateField(verbose_name=_('Дата начала'))
    to_day = models.DateField(verbose_name=_('Дата окончания'), blank=True, null=True)
    is_known = models.BooleanField(verbose_name=_('Подтверждено'), default=True)

    class Meta:
        ordering = ('team', 'from_day', )

    def __str__(self):
        years = '...'
        if self.is_known:
            if not self.to_day:
                years = "с {:%Y}".format(self.from_day)
            else:
                years = "{:%Y}-{:%Y}".format(self.from_day, self.to_day)
        return "{} ({})".format(self.name, years)


class TableRowFields(models.Model):
    place = models.CharField(
        verbose_name=_('Место'), max_length=2, blank=True,
    )
    played = models.PositiveSmallIntegerField(
        verbose_name=_('И'), null=True, blank=True,
        validators=(MaxValueValidator(100),),
    )
    wins = models.PositiveSmallIntegerField(
        verbose_name=_('В'), null=True, blank=True,
        validators=(MaxValueValidator(100),),
    )
    draws = models.PositiveSmallIntegerField(
        verbose_name=_('Н'), null=True, blank=True,
        validators=(MaxValueValidator(100),),
    )
    losses = models.PositiveSmallIntegerField(
        verbose_name=_('П'), null=True, blank=True,
        validators=(MaxValueValidator(100),),
    )
    points = models.PositiveSmallIntegerField(
        verbose_name=_('О'), null=True, blank=True,
        validators=(MaxValueValidator(100),),
    )
    score = models.CharField(
        verbose_name=_('Р/О'), max_length=10, blank=True
    )
    order = models.PositiveSmallIntegerField(
        verbose_name=_('Сортировка'), null=True, blank=True,
        validators=(MaxValueValidator(40),),
    )

    class Meta:
        abstract = True


class GroupSeason(TableRowFields):
    """Representation of each group in a tournament played"""

    name = models.CharField(verbose_name=_('Название команды в группе'),
                            max_length=127, blank=True)
    year = models.PositiveSmallIntegerField(
        verbose_name=_('Год'), blank=True, null=True,
        validators=(MinValueValidator(1900), MaxValueValidator(2100)),
    )
    # both `name` and `year` serves only for simpler repr and sql query
    team = models.ForeignKey(
        Team, verbose_name=_('Команда'), related_name='groups',
    )
    group = models.ForeignKey(
        'matches.Group', verbose_name=_('Группа'),
        related_name='standings'
    )
    story = models.TextField(verbose_name=_('История'), blank=True, )

    class Meta:
        ordering = ('order', '-year', 'team',)
        unique_together = (('team', 'group'),)

    def __str__(self):
        return "{}: {}".format(self.group, self.name)

    def save(self, **kwargs):
        if not self.year:
            self.year = self.group.date_end.year
        if not self.name:
            self.name = self.team.get_name_for(self.year)
        super(GroupSeason, self).save(**kwargs)

    def get_absolute_url(self):
        if self.team_id:
            return self.group.teams.filter(team_id=self.team_id).first().get_absolute_url()


class TeamSeason(TableRowFields):
    """Representation of each tournament a team played"""

    name = models.CharField(verbose_name=_('Название команды в турнире'),
                            max_length=127, blank=True)
    year = models.PositiveSmallIntegerField(
        verbose_name=_('Год'), blank=True, null=True,
        validators=(MinValueValidator(1900), MaxValueValidator(2100)),
    )
    # both `name` and `year` serves only for simpler repr and sql query
    team = models.ForeignKey(
        Team, verbose_name=_('Команда'), related_name='seasons',
    )
    season = models.ForeignKey(
        'matches.Season', verbose_name=_('Турнир'),
        related_name='standings'
    )
    story = models.TextField(verbose_name=_('История'), blank=True, )

    class Meta:
        ordering = ('-year', 'team', 'order')
        unique_together = (('team', 'year', 'season'),)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.year:
            self.year = self.season.date_end.year
        if not self.name:
            team = self.team.get_name_for(self.year)
            self.name = f"{team}: {self.season}"
        super(TeamSeason, self).save(**kwargs)

    def get_absolute_url(self):
        return reverse('teamseason_detail',
                       kwargs={
                           'team_pk': self.team_id,
                           'year': self.year,
                           'pk': self.pk,
                       })

    def get_players(self):
        return self.season._person_seasons.filter(
            team=self.team
        ).select_related(
            'person__tagobject_ptr'
        ).order_by('role', 'person__name')

    def get_matches(self):
        """
        Return all matches for this Season with this Team
        """
        from matches.models import Match
        return Match.objects.filter(
            models.Q(home=self.team) | models.Q(away=self.team)
        ).filter(tourn_season=self.season)

    def get_position(self) -> str:
        total = self.season.participants
        if total:
            pos = self.place or "???"
            return f"{pos} из {total}"
        return "-"


class Person(TagObject):
    first_name = models.CharField(
        max_length=127, verbose_name=_('Имя'), blank=True, )
    middle_name = models.CharField(
        max_length=127, verbose_name=_('Отчество'), blank=True, )
    year_birth = models.PositiveSmallIntegerField(
        verbose_name=_('Год рождения'), blank=True, null=True,
        validators=(MinValueValidator(1900), MaxValueValidator(2100)),
    )
    dob = models.DateField(
        verbose_name=_('Дата рождения'), blank=True, null=True,)
    year_death = models.PositiveSmallIntegerField(
        verbose_name=_('Год смерти'), blank=True, null=True,
        validators=(MinValueValidator(1900), MaxValueValidator(2100)),
    )
    dod = models.DateField(
        verbose_name=_('Дата смерти'), blank=True, null=True,)
    is_dead = models.BooleanField(
        verbose_name=_('Умер'), default=False,
    )

    def __str__(self):
        return "{} {}".format(self.first_name, self.name)

    @property
    def full_name(self):
        return " ".join(filter(bool, [self.name, self.first_name, self.middle_name]))  # noqa

    @property
    def living_years(self):
        birth = self.dob.strftime('%d.%m.%Y') if self.dob else self.year_birth or '???'  # noqa
        death = self.dod.strftime('%d.%m.%Y') if self.dod else self.year_death or '???'  # noqa
        if self.is_dead:
            return "{}-{}".format(birth, death)
        return "{}".format(birth)

    def save(self, **kwargs):
        if self.dob:
            self.year_birth = self.dob.year
        if self.dod:
            self.year_death = self.dod.year
        if self.dod or self.year_death:
            self.is_dead = True
        super(Person, self).save(**kwargs)

    def get_absolute_url(self):
        return reverse('persons_detail', kwargs={'pk': self.pk})


class PersonSeason(models.Model):
    """Representation of each year in a person's career"""
    PROP = '01-prop'
    HOOKER = '02-hooker'
    LOCK = '04-lock'
    BACKROW = '06-backrow'
    SH = '09-scrum-half'
    FH = '10-fly-half'
    CENTER = '12-center'
    WINGER = '14-winger'
    FB = '15-fullback'
    FIRST_ROW = '03-firstrow'
    FORWARD = '08-forward'
    HALF = '10-half'
    BACK = '15-back'
    PLAYER = '20-player'
    REF = '30-referee'
    COACH = '40-coach'

    ROLE_CHOICES = (
        (PLAYER, _('игрок')),
        (PROP, _('1, 3')),
        (HOOKER, _('2')),
        (LOCK, _('4/5')),
        (BACKROW, _('6-8')),
        (SH, _('9')),
        (FH, _('10')),
        (CENTER, _('12/13')),
        (WINGER, _('11/14')),
        (FB, _('15')),
        (FIRST_ROW, _('1-3')),
        (FORWARD, _('1-8')),
        (HALF, _('9-10')),
        (BACK, _('11-15')),
        (REF, _('судья')),
        (COACH, _('тренер')),
    )

    person = models.ForeignKey(
        Person, verbose_name=_('Персона'), related_name='seasons',
    )
    year = models.PositiveSmallIntegerField(
        verbose_name=_('Год'),
        validators=(MinValueValidator(1900), MaxValueValidator(2100)),
    )
    role = models.CharField(
        verbose_name=_('Амплуа'), max_length=127,
        choices=ROLE_CHOICES, default=PLAYER
    )
    team = models.ForeignKey(
        Team, verbose_name=_('Команда'), related_name='_person_seasons',
        blank=True, null=True
    )
    season = models.ForeignKey(
        'matches.Season', verbose_name=_('Розыгрыш турнира'),
        related_name='_person_seasons', blank=True, null=True
    )
    story = models.TextField(verbose_name=_('Комментарий'), blank=True, )

    class Meta:
        ordering = ('-year', 'season', 'role')
        unique_together = (('person', 'year', 'season', 'role'))

    def __str__(self):
        # beware select_related when looping!
        return "{} {}".format(self.person, self.year)

    @property
    def role_verbose(self):
        return dict(self.ROLE_CHOICES).get(self.role)
