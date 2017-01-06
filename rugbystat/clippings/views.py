import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import validate_request, process_user


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
            process_user(uid)
            # TODO: For more robustness, it's a good idea to add the work to a
            # django-rq and process the queue in a worker process.

        return HttpResponse('OK', content_type="text/plain")
