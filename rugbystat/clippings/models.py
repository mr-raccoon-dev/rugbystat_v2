# -*- coding: utf-8 -*-
import re
from datetime import date

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils.deconstruct import deconstructible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel, TitleDescriptionModel
from dropbox.exceptions import ApiError
from dropbox.rest import ErrorResponse

from storages.backends.dropbox import DropBoxStorage
from teams.models import TagObject


def get_dropbox_content_url(url):
    return url.replace('www.dropbox', 'dl.dropboxusercontent')


class Source(models.Model):
    PHOTO = 'photo'
    NEWSPAPER = 'newspaper'
    MAGAZINE = 'magazine'
    PROTOCOL = 'protocol'
    PROGRAM = 'program'
    BOOK = 'book'
    TYPE_CHOICES = (
        (PHOTO, 'photo'),
        (NEWSPAPER, 'newspaper'),
        (MAGAZINE, 'magazine'),
        (PROTOCOL, 'protocol'),
        (PROGRAM, 'program'),
        (BOOK, 'book'),
    )
    title = models.CharField(
        verbose_name=_('Название'), max_length=127, default='N/A')
    type = models.CharField(
        verbose_name=_('Тип'), max_length=127,
        choices=TYPE_CHOICES, default=PHOTO)

    def __str__(self):
        return self.title

    @cached_property
    def documents(self):
        return Document.objects.filter(source__source_id=self.id)

    def as_dict(self):
        result = dict(self.__dict__)
        result.pop('_state')
        return result


class SourceObject(models.Model):
    source = models.ForeignKey(Source, related_name='instances')
    edition = models.CharField(
        verbose_name=_('Название'), max_length=127, blank=True)
    year = models.PositiveSmallIntegerField(
        verbose_name=_('Год'), blank=True, null=True,
        validators=(MinValueValidator(1900), MaxValueValidator(2100)),
    )
    date = models.DateField(verbose_name=_('Дата'), blank=True, null=True)

    def __str__(self):
        if self.edition:
            return "{}, {}".format(self.source, self.edition)
        return self.source

    @cached_property
    def documents(self):
        return self.scans.all()


@deconstructible
class MyDropbox(DropBoxStorage):
    def url(self, name):
        return name


class DocumentQuerySet(models.QuerySet):
    def create_from_meta(self, **kwargs):
        with transaction.atomic():
            metadata = kwargs.get('meta', None)

            if metadata is None:
                return

            fname = metadata.name
            # '1933_name.jpg'
            # '1933name.jpg'
            # '1963-08-001.jpg'
            # '1988_01dd.jpg'
            # '91-03_dd.jpg'
            # '89-12-20filename.jpg'
            # '91-05-06_name.jpg'
            year, month, day, name = re.findall('(\d+)-*(\d*)-*(\d*)_*(.*)',
                                                 fname)[0]
            if len(day) > 2:
                name = day + name
                day = ''

            if month and day:
                doc_date = date(year, month, day)
            else:
                doc_date = None

            # create a Document
            document = self.model(title=name, dropbox=metadata.path_lower,
                                  date=doc_date, year=year, month=month or None, )
            document.save(force_insert=True)
        return document


class Document(TitleDescriptionModel, TimeStampedModel):
    """
    Model of all documents (photos, clips, articles)
    """
    title = models.CharField(
        verbose_name=_('Заголовок'), max_length=127, default='Archive')
    source = models.ForeignKey(
        SourceObject, verbose_name=_('Источник'), related_name='scans',
        blank=True, null=True)
    dropbox = models.FileField(
        verbose_name=_('Путь в Dropbox'), storage=MyDropbox(),
        blank=True, null=True)
    dropbox_path = models.URLField(
        verbose_name=_('Прямая ссылка на файл'), max_length=127, blank=True)
    dropbox_thumb = models.URLField(
        verbose_name=_('Прямая ссылка на превью'), max_length=127, blank=True)
    year = models.PositiveSmallIntegerField(
        verbose_name=_('Год создания'), blank=True, null=True,
        validators=(MinValueValidator(1900), MaxValueValidator(2100)),
    )
    month = models.PositiveSmallIntegerField(
        verbose_name=_('Месяц'), validators=[MaxValueValidator(12)],
        blank=True, null=True)
    date = models.DateField(
        verbose_name=_('Дата'), blank=True, null=True)
    is_image = models.BooleanField(
        verbose_name=_('Этот файл изображение?'), default=False)
    is_deleted = models.BooleanField(
        verbose_name=_('Файл удален?'), default=False)
    versions = models.ManyToManyField('self', verbose_name=_('Версии файла'))
    tag = models.ManyToManyField(
        TagObject, verbose_name=_('Содержит сведения о'))

    objects = DocumentQuerySet.as_manager()

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.client = self.dropbox.storage.client

    @cached_property
    def filename(self):
        return self.dropbox.name.split('/')[-1]

    @cached_property
    def extension(self):
        return self.dropbox.name.split('.')[-1].lower()

    def __str__(self):
        return self.title

    def save(self, **kwargs):

        if not self.dropbox_path and self.dropbox:
            if self.extension in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'gif']:
                self.is_image = True
                self.dropbox_path = self.get_share_link(self.dropbox.name)
                self.dropbox_thumb = self.get_share_link(self.get_thumb_path())
            else:
                self.dropbox_path = self.get_share_link(self.dropbox.name, 
                                                        convert=False)
        super(Document, self).save(**kwargs)

    def get_share_link(self, path, convert=True):
        """
        Return content URL for given path.

        >>> get_share_link('/.thumbs/1928.jpg')
        'https://dl.dropboxusercontent.com/s/xunoyzi0jiz4h9o/1928.jpg?dl=0'

        >>> get_share_link('/1900/1928.pdf')
        'https://www.dropbox.com/s/xunoyzi0jiz4h9o/1928.pdf?dl=0'

        :param path:
        :type path: str
        :return: shared link of a created image
        :rtype: str
        """
        try:
            result = self.client.share(path, False)
            if convert:
                return get_dropbox_content_url(result['url']) 
            else:
                return result['url']
        except ApiError:
            pass
        return None

    def get_thumb_path(self):
        try:
            result = self.client.metadata('/.thumbs/{}'.format(self.filename))
        except ErrorResponse:
            resp, metadata = self.client.thumbnail_and_metadata(self.dropbox.name)
            f = resp.read()
            result = self.client.put_file('/.thumbs/{}'.format(self.filename), f)
        return result['path']
