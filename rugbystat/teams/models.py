from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _


class TagObject(models.Model):
    name = models.CharField(max_length=127, verbose_name=_('Базовое название'))
    story = models.TextField(verbose_name=_('История'))

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


class City(models.Model):
    pass


class Stadium(models.Model):
    city = models.ForeignKey(City, verbose_name=_('Город'))


class Team(TagObject):
    short_name = models.CharField(
        max_length=32, verbose_name=_('Короткое название'), blank=True)
    city = models.ForeignKey(City, verbose_name=_('Город'))
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
        'self', verbose_name=_('Команда-родитель'), blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    def save(self, **kwargs):
        if not self.short_name:
            self.short_name = "{} {}".format(self.name, self.city.short_name)
        super(Team, self).save(**kwargs)


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
