# coding: utf-8

import copy
import os
import shutil
import time
import traceback
from typing import Optional, Tuple, List, Dict

from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction, Error as BaseDatabaseError
from django.utils import timezone
from youtube_dl import YoutubeDL
from youtube_dl.postprocessor.common import PostProcessor

from rls.models import Release
from rls.utils import hash_file
from rlscloud import app
from rlsget.models import DownloadTask


log = get_task_logger(__name__)


class YoutubeDLTask(app.Task):
    RESERVED_YOUTUBE_DL_OPTIONS = ('quiet', 'noplaylist', 'outtmpl', 'progress_hooks')

    YOUTUBE_DL_OPTIONS = {
        'quiet': True,
        'noplaylist': True,
        'outtmpl': os.path.join(settings.INCOMING_DIR, '{0}_%(title)s.%(ext)s'),
    }

    ignore_result = True

    def _clean_options(self, options: dict) -> dict:
        for reserved_option in self.RESERVED_YOUTUBE_DL_OPTIONS:
            options.pop(reserved_option, None)
        return options

    def _progress_hook(self, status: dict) -> None:
        if not self.request.called_directly:
            self._last_status = status
            if status['status'] == 'downloading':
                self.update_state(state='PROGRESS', meta=status)
            elif status['status'] == 'finished':
                with transaction.atomic():
                    self.download_task.state = DownloadTask.PROCESSING
                    self.download_task.save()

    def _hash_progress_hook(self, size: int, position: int) -> None:
        try:
            if time.time() - self._hash_start > 1000:
                self.update_state(state='PROGRESS', meta={
                    'status': 'downloading',
                    'total_bytes': size,
                    'downloaded_bytes': position
                })
            else:
                self._hash_start = time.time()
        except AttributeError:
            self._hash_start = time.time()

    def _get_postprocessor(self):
        parent = self

        class YoutubeDLTaskPostprocessor(PostProcessor):
            def run(self, information: dict) -> Tuple[List, Dict]:
                download_task = parent.download_task

                name = information['title']
                source = information['filepath']
                file_hash = hash_file(source, progress_hook=parent._hash_progress_hook)
                media_destination = os.path.join(settings.RELEASE_DIR, file_hash + os.path.splitext(source)[-1])
                absolute_destination = os.path.join(settings.MEDIA_ROOT, media_destination)

                # TODO: Check if file already exists
                shutil.move(source, absolute_destination)

                # TODO: This doesn't rolls back
                with transaction.atomic():
                    release = Release()
                    release.name = name
                    release.file = media_destination
                    release.created_by = download_task.created_by
                    release.file_hash = file_hash
                    release.save()

                    download_task.state = DownloadTask.FINISHED
                    download_task.finished_at = timezone.now()
                    download_task.release = release
                    download_task.save()

                return super().run(information)
        return YoutubeDLTaskPostprocessor()

    def run(self, release_task_pk: int, custom_options: Optional[dict]=None) -> None:
        try:
            with transaction.atomic():
                self.download_task = DownloadTask.objects.get(pk=release_task_pk)
                self.download_task.downloader = DownloadTask.YOUTUBE_DL
                self.download_task.celery_id = self.request.id
                self.download_task.state = DownloadTask.DOWNLOADING
                self.download_task.started_at = timezone.now()
                self.download_task.save()

            options = copy.deepcopy(self.YOUTUBE_DL_OPTIONS)
            options['outtmpl'] = options['outtmpl'].format(self.request.id.replace('-', ''))
            options['progress_hooks'] = [self._progress_hook]

            if custom_options:
                custom_options = self._clean_options(custom_options)
                options.update(custom_options)

            downloader = YoutubeDL(options)
            downloader.add_post_processor(self._get_postprocessor())
            downloader.download([self.download_task.url])
        except SystemExit:
            try:
                os.remove(self._last_status['tmpfilename'])
            except AttributeError:
                return
            except:
                log.exception('Exception while removing temporary file. id={0}, tempfilename={1}'.format(
                        release_task_pk, self._last_status['tmpfilename'])
                )
                raise
        except (BaseDatabaseError, ObjectDoesNotExist, MultipleObjectsReturned):
            # Hope we've caught everything
            log.exception('Exception while updating DownloadTask. id={0}'.format(release_task_pk))
            raise
        except:
            try:
                with transaction.atomic():
                    self.download_task.state = DownloadTask.ERROR
                    self.download_task.finished_at = timezone.now()
                    self.download_task.save()

                    self.download_task.tracebacks.create(text=traceback.format_exc())
                raise
            except (BaseDatabaseError, ObjectDoesNotExist, MultipleObjectsReturned):
                log.exception('Exception while changing DownloadTask.state to ERROR. id={0}'.format(release_task_pk))
                raise

youtube_dl = YoutubeDLTask()
