import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import validate_request


logger = logging.getLogger('django.request')


@csrf_exempt
def import_from_dropbox(request):
    if request.method == 'GET':
        challenge = request.GET.get('challenge')
        return HttpResponse(challenge, content_type="text/plain")
    else:
        if not validate_request(request):
            return HttpResponse('False', content_type="text/plain")

        req = json.loads(request.body.decode('UTF-8'))
        logger.debug('Got dropbox request')
        logger.debug(str(req))
        for uid in req['delta']['users']:
            # We need to respond quickly to the webhook request,
            # so we do the actual work in a separate thread.
            fname = '{}/{}.lock'.format(settings.BASE_DIR, uid)
            logger.debug('Try to create {}'.format(fname))
            open(fname, 'a').close()
            logger.debug('Created')
            # TODO: For more robustness, it's a good idea to add the work to a
            # django-rq and process the queue in a worker process.

        return HttpResponse('OK', content_type="text/plain")
