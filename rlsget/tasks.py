# coding: utf-8

import copy
from typing import Any, Optional

from celery.utils.log import get_task_logger
from youtube_dl import YoutubeDL

from rlscloud import app
from rlsget.models import ReleaseDownloadFile


log = get_task_logger(__name__)


class YoutubeDLTask(app.Task):
    RESERVED_YOUTUBE_DL_OPTIONS = ('quiet', 'noplaylist', 'progress_hooks')

    YOUTUBE_DL_OPTIONS = {
        'quiet': True,
        'noplaylist': True,
    }

    ignore_result = True

    def _finished(self):
        self.download_file.state = ReleaseDownloadFile.FINISHED
        self.download_file.save()

    def _clean_options(self, options: dict) -> dict:
        for reserved_option in self.RESERVED_YOUTUBE_DL_OPTIONS:
            options.pop(reserved_option, None)
        return options

    def _progress_hook(self, status: dict) -> None:
        if not self.request.called_directly:
            if status['status'] == 'downloading':
                self.update_state(state='PROGRESS', meta=status)
            elif status['status'] == 'finished':
                self._finished()

    def run(self, download_file_pk: int, custom_options: Optional[dict]=None) -> None:
        if not isinstance(download_file_pk, int):
            raise ValueError('You must the primary key of a ReleaseDownloadFile object')

        self.download_file = ReleaseDownloadFile.objects.get(pk=download_file_pk)
        self.download_file.celery_task = self.request.id
        self.download_file.state = ReleaseDownloadFile.DOWNLOADING
        self.download_file.save()

        options = copy.deepcopy(self.YOUTUBE_DL_OPTIONS)
        options['progress_hooks'] = [self._progress_hook]

        if custom_options:
            custom_options = self._clean_options(custom_options)
            options.update(custom_options)

        downloader = YoutubeDL(options)
        downloader.download([self.download_file.source])
