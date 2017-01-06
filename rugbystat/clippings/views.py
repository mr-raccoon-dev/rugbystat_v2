import hmac
import json
import re
import threading
from hashlib import sha256
from datetime import date

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import redis
from dropbox.client import DropboxClient

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
    return signature == hmac.new(settings.DROPBOX_ACCESS_TOKEN, request.data,
                                 sha256).hexdigest()


def process_user(uid):
    """Call /delta for the given user ID and process any changes."""

    # OAuth token for the user
    token = redis_client.hget('tokens', uid)

    # /delta cursor for the user (None the first time)
    cursor = redis_client.hget('cursors', uid)

    client = DropboxClient(token)
    has_more = True

    while has_more:
        result = client.delta(cursor)

        for path, metadata in result['entries']:
            fname = path.split('/')[-1]
            # '1933_name.jpg'
            # '1933name.jpg'
            # '1963-08-001.jpg'
            # '1988_01dd.jpg'
            # '91-03_dd.jpg'
            # '89-12-20filename.jpg'
            # '91-05-06_name.jpg'
            year, month, day, name = re.findall('(\d+)-*(\d*)-*(\d*)_*(.*)',
                                                 fname)
            if len(day) > 2:
                name = day + name
                day = ''

            if month and day:
                doc_date = date(year, month, day)
            else:
                doc_date = None

            # Ignore deleted files, folders
            if metadata is None or metadata['is_dir']:
                continue
            # create a Document
            Document.objects.create(title=name, dropbox=path, date=doc_date, 
                                    year=year, month=month, )

        # Update cursor
        cursor = result['cursor']
        redis_client.hset('cursors', uid, cursor)

        # Repeat only if there's more to do
        has_more = result['has_more']


@csrf_exempt
def import_from_dropbox(request):
    if request.method == 'GET':
        challenge = request.GET.get('challenge')
        return HttpResponse(challenge, content_type="text/plain")
    else:
        if not validate_request(request):
            return HttpResponse('False', content_type="text/plain")
        for uid in json.loads(request.body)['delta']['users']:
            # We need to respond quickly to the webhook request, so we do the
            # actual work in a separate thread.
            threading.Thread(target=process_user, args=(uid,)).start()
            # TODO: For more robustness, it's a good idea to add the work to a
            # queue and process the queue in a worker process.

        return HttpResponse('OK', content_type="text/plain")
