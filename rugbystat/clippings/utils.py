import hmac
from hashlib import sha256

from django.conf import settings
from django.core.cache import cache

from dropbox import Dropbox
from dropbox.files import FolderMetadata, DeletedMetadata

from .models import Document


__author__ = 'krnr'


# try:
#     redis_client = redis.from_url(settings.BROKER_URL)
# except:
#     redis_client = settings.RSL


import logging
logger = logging.getLogger('django.request')


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
    logger.debug('Processing folder: ' + folder)

    cursor = cache.get(folder)
    # cursor = redis_client.hget('cursors', folder)
    logger.debug('Cursor: ' + repr(cursor))
    has_more = True

    while has_more:
        if cursor is None:
            result = dbx.files_list_folder(folder)
        else:
            result = dbx.files_list_folder_continue(cursor)

        logger.debug('New cursor: ' + str(result.cursor))
        logger.debug('Has {} elements'.format(len(result.entries)))
        logger.debug('Has more: ' + str(result.has_more))

        for metadata in result.entries:
            logger.debug('\nGot metadata:')
            logger.debug(metadata)

            # Ignore enclosed folders
            if isinstance(metadata, FolderMetadata):
                continue

            # Update deleted files
            if isinstance(metadata, DeletedMetadata):
                Document.objects.filter(dropbox=metadata.path_lower).update(
                    is_deleted=True)
                logger.debug('We found deleted documents: ' +
                             repr(Document.objects.filter(dropbox=metadata.path_lower)))
                continue

            # Create documents from every file
            if not Document.objects.filter(title=metadata.name).count():
                document = Document.objects.create_from_meta(meta=metadata)
                logger.debug('Created: ' + repr(document))

        # Update cursor
        cursor = result.cursor
        cache.set(folder, cursor)

        # Repeat only if there's more to do
        has_more = result.has_more


def process_user(uid):
    """Call endpoint for every folder and look for any changes."""
    token = cache.get(uid) or settings.DROPBOX_ACCESS_TOKEN
    dbx = Dropbox(token)
    logger.info("Dropbox instance: " + repr(dbx))

    result = dbx.files_list_folder(path='')
    for metadata in result.entries:
        if isinstance(metadata, FolderMetadata) and metadata.name != '.thumbs':
            logger.debug(metadata)
            logger.debug("Passing to process_folder()")
            process_folder(metadata, dbx)
