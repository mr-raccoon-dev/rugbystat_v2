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

    def save(self, **kwargs):
        super(Document, self).save(**kwargs)
        if not self.dropbox_thumb:
            self.save_thumb()

    def save_share_link(self):
        try:
            result = self.dropbox.storage.client.share(self.dropbox.name, False)
            self.dropbox_path = get_dropbox_content_url(result['url'])
        except ApiError:
            pass

    def save_thumb(self):
        resp, metadata = self.dropbox.storage.client.thumbnail_and_metadata(self.dropbox.name)
        f = resp.read()
        result = self.dropbox.storage.client.put_file('/.thumbs/{}'.format(
            self.filename), f)
        self.dropbox_thumb = get_dropbox_content_url(result['url'])

    @cached_property
    def filename(self):
        return self.dropbox.name.split('/')[-1]
