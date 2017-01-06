import hmac
import json
import re
import threading
from hashlib import sha256
from datetime import date

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dropbox.files import FolderMetadata, DeletedMetadata

import redis
from dropbox import Dropbox

from clippings.models import Document


try:
    redis_client = redis.from_url(settings.BROKER_URL)
except:
    redis_client = settings.RSL


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
    cursor = redis_client.hget('cursors', folder)
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
        redis_client.hset('cursors', folder, cursor)

        # Repeat only if there's more to do
        has_more = result.has_more


def process_user(uid):
    """Call endpoint for every folder and look for any changes."""

    token = redis_client.hget('tokens', uid) or settings.DROPBOX_ACCESS_TOKEN
    dbx = Dropbox(token)

    result = dbx.files_list_folder(path='')
    for metadata in result.entries:
        if isinstance(metadata, FolderMetadata) and metadata.name != '.thumbs':
            process_folder(metadata, dbx)


@csrf_exempt
def import_from_dropbox(request):
    if request.method == 'GET':
        challenge = request.GET.get('challenge')
        return HttpResponse(challenge, content_type="text/plain")
    else:
        if not validate_request(request):
            return HttpResponse('False', content_type="text/plain")

        req = json.loads(request.body.decode('UTF-8'))
        for uid in req['delta']['users']:
            # We need to respond quickly to the webhook request, so we do the
            # actual work in a separate thread.
            threading.Thread(target=process_user, args=(uid,)).start()
            # TODO: For more robustness, it's a good idea to add the work to a
            # queue and process the queue in a worker process.

        return HttpResponse('OK', content_type="text/plain")
