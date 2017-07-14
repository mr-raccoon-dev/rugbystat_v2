from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _


class TagObject(models.Model):
    name = models.CharField(max_length=127, verbose_name=_('Базовое название'))
    story = models.TextField(verbose_name=_('История'), blank=True, )

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
    
    def __str__(self):
        return self.short_name or self.name
    
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


class Person(TagObject):
    first_name = models.CharField(
        max_length=127, verbose_name=_('Имя'), blank=True, )
    middle_name = models.CharField(
        max_length=127, verbose_name=_('Отчество'), blank=True, )
    year = models.PositiveSmallIntegerField(
        verbose_name=_('Год рождения'), blank=True, null=True,
        validators=(MinValueValidator(1900), MaxValueValidator(2100)),
    )
    dob = models.DateField(
        verbose_name=_('Дата рождения'), blank=True, null=True,)

    def __str__(self):
        return "{} {}".format(self.first_name, self.name)


class PersonSeason(models.Model):
    """Representation of each year in a person's career"""
    PLAYER = 'player'
    PROP = 'prop'
    HOOKER = 'hooker'
    LOCK = 'lock'
    BACKROW = 'backrow'
    SH = 'scrum-half'
    FH = 'fly-half'
    CENTER = 'center'
    WINGER = 'winger'
    FB = 'fullback'
    REF = 'referee'
    COACH = 'coach'
    
    ROLE_CHOICES = (
        (PLAYER, _('игрок')),
        (PROP, _('1/3')),
        (HOOKER, _('2')),
        (LOCK, _('4/5')),
        (BACKROW, _('6-8')),
        (SH, _('9')),
        (FH, _('10')),
        (CENTER, _('12/13')),
        (WINGER, _('11/14')),
        (FB, _('15')),
        (REF, _('судья')),
        (COACH, _('тренер')),
    )

    person = models.ForeignKey(
        Person, verbose_name=_('Персона'), related_name='seasons', )
    year = models.PositiveSmallIntegerField(
        verbose_name=_('Год'),
        validators=(MinValueValidator(1900), MaxValueValidator(2100)),
    )
    role = models.CharField(
        verbose_name=_('Тип'), max_length=127,
        choices=ROLE_CHOICES, default=PLAYER)
    team = models.ForeignKey(
        Team, verbose_name=_('Команда'), related_name='_person_seasons', 
        blank=True, null=True
    )
    story = models.TextField(verbose_name=_('История'), blank=True, )

    def __str__(self):
        return "{} {}".format(self.person, self.year)
