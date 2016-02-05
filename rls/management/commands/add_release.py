# coding: utf-8

import os
import shutil

from django.conf import settings
from django.core.management import BaseCommand
from django.contrib.auth import get_user_model

from rls.models import Release
from rls.utils import hash_file

User = get_user_model()


class Command(BaseCommand):
    help = 'Adds a file to rlscloud in the name of an existing user'

    def add_arguments(self, parser):
        parser.add_argument('username', help='Username')
        parser.add_argument('password', help='Password')
        parser.add_argument('path', help='File path', nargs='+')

    def _exit(self, msg, code=1):
        self.stderr.write('Error: ' + msg)
        exit(code)

    def _print(self, msg, prefix='+'):
        self.stdout.write('[{0}] {1}'.format(prefix, msg))

    def add_file(self, user, file):
        self._print('Hashing {0!r}'.format(file))
        file_hash = hash_file(file)
        self._print('MD5: {0}'.format(file_hash), '-')

        name, extension = os.path.splitext(file)
        name = os.path.basename(name)

        media_destination = os.path.join(settings.RELEASE_DIR, file_hash + extension)
        absolute_destination = os.path.join(settings.MEDIA_ROOT, media_destination)

        release = Release()
        release.name = name
        release.file = media_destination
        release.created_by = user
        release.file_hash = file_hash
        release.save()

        self._print('Release ID: {0}'.format(release.pk))
        self._print('Copying {0!r} to {1!r}'.format(file, absolute_destination))
        shutil.copy(file, absolute_destination)

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        files = options['path']

        try:
            user = User.objects.get(username=username)
            valid = user.check_password(password)
        except User.DoesNotExist:
            self._exit('User {0!r} does not exits.'.format(username))
            return
        else:
            if not valid:
                self._exit('Invalid password')
                return
            else:
                for file in files:
                    self.add_file(user, file)
