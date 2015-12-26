# coding: utf-8

import os

from celery.result import AsyncResult
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class DownloadTask(models.Model):
    QUEUED = 0
    DOWNLOADING = 1
    FINISHED = 2
    ERROR = 3
    PROCESSING = 4

    STATE_CHOICES = (
        (QUEUED, _('Queued')),
        (DOWNLOADING, _('Downloading')),
        (FINISHED, _('Finished')),
        (ERROR, _('Error')),
        (PROCESSING, _('Processing'))
    )

    FROM_YOUTUBE_DL = 0
    FROM_FFMPEG = 1

    SOURCE_CHOICES = (
        (FROM_YOUTUBE_DL, _('From youtube-dl')),
        (FROM_FFMPEG, _('From ffmpeg'))
    )

    url = models.TextField()
    source = models.PositiveSmallIntegerField(choices=SOURCE_CHOICES, null=True)
    is_hidden = models.BooleanField(default=False)
    celery_task = models.UUIDField(null=True)
    state = models.PositiveSmallIntegerField(choices=STATE_CHOICES, default=QUEUED)
    release = models.OneToOneField('rls.Release', null=True)

    elapsed = models.FloatField(default=0)
    size = models.PositiveIntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        ordering = ('-created_at', )

    def async_result(self):
        return AsyncResult(str(self.celery_task))

    def as_dict(self) -> dict:
        result = {
            'state': self.state,
            'url': self.url,
            'id': self.celery_task,
            'created_at': self.created_at,
            'source': self.source
        }

        if self.state == self.DOWNLOADING:
            info = self.async_result().info
            if info:
                result.update({
                    'total': info['total_bytes'],
                    'downloaded': info['downloaded_bytes'],
                    'elapsed': info['elapsed'],
                    'filename': os.path.basename(info['filename'])
                })
        elif self.state == self.FINISHED:
            result.update({
                'total': self.size,
                'downloaded': self.size,
                'elapsed': self.elapsed,
                'filename': os.path.basename(self.release.file.name)
            })
        return result
