from django.db import models
from django.utils.functional import cached_property
from django_extensions.db.models import TimeStampedModel
from dropbox.exceptions import ApiError


def get_dropbox_content_url(param):
    return param.replace('www.dropbox', 'dl.dropboxusercontent')


class Document(TimeStampedModel):
    title = models.CharField(max_length=127, default='Archive')
    dropbox = models.FileField(blank=True, null=True)
    dropbox_path = models.URLField(max_length=127, blank=True)
    dropbox_thumb = models.URLField(max_length=127, blank=True)

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.client = self.dropbox.storage.client

    def save(self, **kwargs):
        if not self.dropbox_path and self.dropbox:
            self.dropbox_path = self.get_share_link(self.dropbox.name)
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
        resp, metadata = self.client.thumbnail_and_metadata(self.dropbox.name)
        f = resp.read()
        result = self.client.put_file('/.thumbs/{}'.format(self.filename), f)
        return result['path']

    @cached_property
    def filename(self):
        return self.dropbox.name.split('/')[-1]
