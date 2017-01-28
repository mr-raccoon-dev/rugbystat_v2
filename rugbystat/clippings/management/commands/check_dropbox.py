import os

from django.conf import settings
from django.core.management import BaseCommand

from clippings.utils import process_user


class Command(BaseCommand):
    def handle(self, *args, **options):
        os.chdir(settings.BASE_DIR)
        locks = [file for file in os.listdir() if '.lock' in file]
        if locks:
            # grab the first lock if exists
            filename = locks[0] 
            uid = int(filename.split('.')[0])
            process_user(uid)
            os.remove(filename)
