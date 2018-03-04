from django.core.management import BaseCommand

from gettextutils.utils import (
    find_translatable_files, select_translatable_strings
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        files_list = find_translatable_files()
        self.stdout.write(f'Files list {files_list}')

        msgs, errors = select_translatable_strings(files_list)
        self.stdout.write(f'Messages {msgs}')
