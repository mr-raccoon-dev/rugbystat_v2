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
    OTHER = 'other'
    TYPE_CHOICES = (
        (PHOTO, 'фото'),
        (NEWSPAPER, 'газета'),
        (MAGAZINE, 'журнал'),
        (PROTOCOL, 'протокол'),
        (PROGRAM, 'программка'),
        (BOOK, 'книга'),
        (OTHER, 'прочее'),
    )
    title = models.CharField(
        verbose_name=_('Название'), max_length=127, default='N/A')
    kind = models.CharField(
        verbose_name=_('Тип'), max_length=127,
        choices=TYPE_CHOICES, default=PHOTO)

    class Meta:
        ordering = ('title', 'id', )

    def __str__(self):
        return self.title

    @cached_property
    def documents(self):
        return self.scans.not_deleted().prefetch_related('versions')

    def as_dict(self):
        result = dict(self.__dict__)
        result.pop('_state')
        return result


class SourceObjectManager(models.Manager):
    def get_queryset(self):
        qs = super(SourceObjectManager, self).get_queryset()
        return qs.select_related('source')


class SourceObject(models.Model):
    source = models.ForeignKey(Source, related_name='instances')
    edition = models.CharField(
        verbose_name=_('Название'), max_length=127, blank=True)
    year = models.PositiveSmallIntegerField(
        verbose_name=_('Год'), blank=True, null=True,
        validators=(MinValueValidator(1900), MaxValueValidator(2100)),
    )
    date = models.DateField(verbose_name=_('Дата'), blank=True, null=True)

    objects = SourceObjectManager()

    class Meta:
        ordering = ('source', 'year', )

    def __str__(self):
        if self.edition and not self.source.kind == Source.BOOK:
            return "{} {}, {}".format(
                self.source.title, self.edition, self.year)
        return self.source.title

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

            if len(year) < 4:
                year = '19' + year

            if month and day and int(day) > 0:
                try:
                    doc_date = date(int(year), int(month), int(day))
                except:
                    doc_date = None
            else:
                doc_date = None

            # create a Document
            document = self.model(title=fname, dropbox=metadata.path_lower,
                                  date=doc_date, year=year, month=month or None, )
            document.save(force_insert=True)
        return document

    def not_deleted(self):
        return self.filter(is_deleted=False)


class Document(TitleDescriptionModel, TimeStampedModel):
    """
    Model of all documents (photos, clips, articles)
    """
    title = models.CharField(
        verbose_name=_('Заголовок'), max_length=127, default='Archive')
    source = models.ForeignKey(
        Source, verbose_name=_('Источник'), related_name='scans',
        blank=True, null=True)
    source_issue = models.ForeignKey(
        SourceObject, verbose_name=_('Выпуск'), related_name='scans',
        blank=True, null=True)
    kind = models.CharField(
        verbose_name=_('Тип'), max_length=127,
        choices=Source.TYPE_CHOICES, 
        blank=True)
    dropbox = models.FileField(
        verbose_name=_('Путь в Dropbox'), storage=MyDropbox(),
        blank=True, null=True)
    dropbox_path = models.URLField(
        verbose_name=_('Прямая ссылка на файл'), max_length=127, blank=True)
    dropbox_thumb = models.URLField(
        verbose_name=_('Прямая ссылка на превью'), max_length=127, 
        blank=True, null=True)
    year = models.PositiveSmallIntegerField(
        verbose_name=_('Год создания'), blank=True, null=True,
        validators=(MinValueValidator(1800), MaxValueValidator(2100)),
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
    versions = models.ManyToManyField(
        'self', verbose_name=_('Версии файла'), blank=True, )
    tag = models.ManyToManyField(
        TagObject, verbose_name=_('Содержит сведения о'), blank=True, )

    objects = DocumentQuerySet.as_manager()

    class Meta:
        ordering = ('year', 'month', 'title' )

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

        if not self.kind and self.source:
            self.kind = self.source.kind

        super(Document, self).save(**kwargs)

    def delete(self, **kwargs):
        self.client.file_delete(self.dropbox.name)
        super(Document, self).delete(**kwargs)

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
        except ErrorResponse:
            # link exists, but file - doesn't
            pass
        return None

    def get_thumb_path(self):
        try:
            meta = self.client.metadata('/.thumbs/{}'.format(self.filename))
            result = meta['path']
            if meta.get('is_deleted'):
                result = self.create_dropbox_thumb()
        except ErrorResponse:
            result = self.create_dropbox_thumb()
        return result

    def create_dropbox_thumb(self):
        resp, metadata = self.client.thumbnail_and_metadata(self.dropbox.name)
        f = resp.read()
        result = self.client.put_file('/.thumbs/{}'.format(self.filename), f)
        return result['path']

    def move(self, to_path):
        """
        Calls file_move(from_path, to_path) method of dropbox.client.DropboxClient instance
    
        Parameters
            from_path
              The path to the file or folder to be moved.
            to_path
              The destination path of the file or folder to be moved.
              This parameter should include the destination filename (e.g. if
              ``from_path`` is ``'/test.txt'``, ``to_path`` might be
              ``'/dir/test.txt'``). If there's already a file at the
              ``to_path`` it will raise an ErrorResponse.
        
        Returns
              A dictionary containing the metadata of the new copy of the file or folder.
        
              For a detailed description of what this call returns, visit:
              https://www.dropbox.com/developers/core/docs#fileops-move
        
        Raises
              A :class:`dropbox.rest.ErrorResponse` with an HTTP status of:
        
              - 400: Bad request (may be due to many things; check e.error for details).
              - 403: An invalid move operation was attempted
                (e.g. there is already a file at the given destination,
                or moving a shared folder into a shared folder).
              - 404: No file was found at given from_path.
              - 503: User over storage quota.
        """
        try:
            self.client.file_move(self.dropbox.name, to_path)
        except ErrorResponse:
            # TODO log error
            pass

        self.dropbox.name = to_path
        self.dropbox_path = self.get_share_link(self.dropbox.name)
        self.dropbox_thumb = self.get_share_link(self.get_thumb_path())
        self.title = self.filename
