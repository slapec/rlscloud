# coding: utf-8

import copy
import os
from typing import Optional

import requests
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db import transaction
from youtube_dl import YoutubeDL
from youtube_dl.postprocessor.common import PostProcessor

from rlscloud import app
from rls.models import Release
from rlsget.models import DownloadTask


log = get_task_logger(__name__)


class YoutubeDLTask(app.Task):
    RESERVED_YOUTUBE_DL_OPTIONS = ('quiet', 'noplaylist', 'progress_hooks')

    YOUTUBE_DL_OPTIONS = {
        'quiet': True,
        'noplaylist': True,
        'outtmpl': settings.YOUTUBE_DL_TEMPLATE
    }

    ignore_result = True

    def _clean_options(self, options: dict) -> dict:
        for reserved_option in self.RESERVED_YOUTUBE_DL_OPTIONS:
            options.pop(reserved_option, None)
        return options

    def _progress_hook(self, status: dict) -> None:
        if not self.request.called_directly:
            self._last_progress = status
            if status['status'] == 'downloading':
                self.update_state(state='PROGRESS', meta=status)
            elif status['status'] == 'finished':
                with transaction.atomic():
                    self.download_task.state = DownloadTask.PROCESSING
                    self.download_task.save()

    def _pre_check(self) -> None:
        requests.get(self.download_task.url, headers={
            'User-Agent': settings.USER_AGENT
        })

    def _get_postprocessor(self) -> PostProcessor:
        parent = self

        class YoutubeDLTaskPostprocessor(PostProcessor):
            def run(self, information):
                download_task = parent.download_task

                if hasattr(parent, '_last_progress'):
                    with transaction.atomic():
                        # TODO: This doesn't rolls back
                        release = Release()
                        release.title = information['title']
                        release.file = information['filepath']
                        release.created_by = download_task.created_by
                        release.save()

                        download_task.state = DownloadTask.FINISHED
                        download_task.release = release
                        download_task.elapsed = parent._last_progress['elapsed']
                        download_task.size = parent._last_progress['total_bytes']
                        download_task.save()
                return super(YoutubeDLTaskPostprocessor, self).run(information)
        return YoutubeDLTaskPostprocessor()

    def run(self, release_task_pk: int, custom_options: Optional[dict]=None) -> None:
        with transaction.atomic():
            self.download_task = DownloadTask.objects.get(pk=release_task_pk)
            self.download_task.source = DownloadTask.FROM_YOUTUBE_DL
            self.download_task.celery_task = self.request.id
            self.download_task.state = DownloadTask.DOWNLOADING
            self.download_task.save()

        try:
            self._pre_check()

            options = copy.deepcopy(self.YOUTUBE_DL_OPTIONS)
            options['progress_hooks'] = [self._progress_hook]

            if custom_options:
                custom_options = self._clean_options(custom_options)
                options.update(custom_options)

            downloader = YoutubeDL(options)
            downloader.add_post_processor(self._get_postprocessor())
            downloader.download([self.download_task.url])
        except Exception as e:
            self.download_task.state = DownloadTask.ERROR
            self.download_task.save()
            raise

youtube_dl = YoutubeDLTask()
