import hmac
from hashlib import sha256

from django.conf import settings
from django.core.cache import cache

import redis
from dropbox import Dropbox
from dropbox.files import FolderMetadata, DeletedMetadata

from .models import Document


__author__ = 'krnr'


# try:
#     redis_client = redis.from_url(settings.BROKER_URL)
# except:
#     redis_client = settings.RSL


def validate_request(request):
    """
    Validate that the request is properly signed by Dropbox.
    (If not, this is a spoofed webhook.)
    """

    signature = request.META.get('HTTP_X_DROPBOX_SIGNATURE')
    return signature == hmac.new(settings.DROPBOX_APP_SECRET.encode('UTF-8'),
                                 request.body, sha256).hexdigest()


def process_folder(metadata, dbx):
    """Call endpoint for a given folder and process any changes."""
    folder = metadata.path_lower
    # /delta cursor for the folder (None the first time)
    cursor = cache.get(folder)
    # cursor = redis_client.hget('cursors', folder)
    has_more = True

    while has_more:
        if cursor is None:
            result = dbx.files_list_folder(metadata.path_lower)
        else:
            result = dbx.files_list_folder_continue(cursor)

        for metadata in result.entries:
            # Ignore enclosed folders
            if isinstance(metadata, FolderMetadata):
                continue

            # Update deleted files
            if isinstance(metadata, DeletedMetadata):
                Document.objects.filter(dropbox=metadata.path_lower).update(
                    is_deleted=True)
                continue

            # Create documents from every file
            Document.objects.create_from_meta(meta=metadata)

        # Update cursor
        cursor = result.cursor
        cache.set(folder, cursor)

        # Repeat only if there's more to do
        has_more = result.has_more


def process_user(uid):
    """Call endpoint for every folder and look for any changes."""

    token = cache.get(uid) or settings.DROPBOX_ACCESS_TOKEN
    dbx = Dropbox(token)

    result = dbx.files_list_folder(path='')
    for metadata in result.entries:
        if isinstance(metadata, FolderMetadata) and metadata.name != '.thumbs':
            process_folder(metadata, dbx)
