from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.functional import cached_property
from django_extensions.db.models import TimeStampedModel
from dropbox.exceptions import ApiError
from dropbox.rest import ErrorResponse


def get_dropbox_content_url(url):
    return url.replace('www.dropbox', 'dl.dropboxusercontent')

# TODO: tags for Document: match, player, team


class Document(TimeStampedModel):
    """
    Model of all documents (photos, clips, articles)
    """
    title = models.CharField(
        verbose_name='Заголовок', max_length=127, default='Archive')
    dropbox = models.FileField(
        verbose_name='Путь в Dropbox', blank=True, null=True)
    dropbox_path = models.URLField(
        verbose_name='Прямая ссылка на файл', max_length=127, blank=True)
    dropbox_thumb = models.URLField(
        verbose_name='Прямая ссылка на превью', max_length=127, blank=True)
    year = models.PositiveIntegerField(
        verbose_name='Год', blank=True, null=True)
    month = models.PositiveSmallIntegerField(
        verbose_name='Месяц', validators=[MaxValueValidator(12)],
        blank=True, null=True)
    date = models.DateField(
        verbose_name='Дата', blank=True, null=True)
    is_image = models.BooleanField(
        verbose_name='Этот файл изображение', default=False)
    versions = models.ManyToManyField('self', verbose_name='Версии файла')

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.client = self.dropbox.storage.client

    @cached_property
    def filename(self):
        return self.dropbox.name.split('/')[-1]

    @cached_property
    def extension(self):
        return self.dropbox.name.split('.')[-1].lower()

    def save(self, **kwargs):
        if not self.dropbox_path and self.dropbox:
            self.dropbox_path = self.get_share_link(self.dropbox.name)
        if self.extension in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'gif']:
            self.is_image = True
            if not self.dropbox_thumb and self.dropbox:
                self.dropbox_thumb = self.get_share_link(self.get_thumb_path())
        super(Document, self).save(**kwargs)

    def get_share_link(self, path):
        """
        Return content URL for given path.

        >>> get_share_link('/.thumbs/1928.jpg')
        'https://dl.dropboxusercontent.com/s/xunoyzi0jiz4h9o/1928.jpg?dl=0'

        :param path:
        :type path: str
        :return: shared link of a created image
        :rtype: str
        """
        try:
            result = self.client.share(path, False)
            return get_dropbox_content_url(result['url'])
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
