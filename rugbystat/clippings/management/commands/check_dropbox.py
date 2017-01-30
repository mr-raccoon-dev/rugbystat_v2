import os
import logging

from django.conf import settings
from django.core.management import BaseCommand

from clippings.utils import process_user


logger = logging.getLogger('django.request')


class Command(BaseCommand):
    def handle(self, *args, **options):
        os.chdir(settings.BASE_DIR)
        locks = [file for file in os.listdir() if '.lock' in file]
        logger.debug('Got following locks in dir: {}'.format(locks))
        if locks:
            # grab the first lock if exists
            filename = locks[0] 
            uid = int(filename.split('.')[0])
            process_user(uid)
            logger.debug('Removing lock {}'.format(filename))
            os.remove(filename)
