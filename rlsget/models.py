# coding: utf-8

import os

from celery.result import AsyncResult
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _


class DownloadTask(models.Model):
    QUEUED = 0
    DOWNLOADING = 1
    PROCESSING = 2
    FINISHED = 3
    ERROR = 4

    STATE_CHOICES = (
        (QUEUED, _('Queued')),
        (DOWNLOADING, _('Downloading')),
        (PROCESSING, _('Processing')),
        (FINISHED, _('Finished')),
        (ERROR, _('Error'))
    )

    YOUTUBE_DL = 0

    DOWNLOADER_CHOICES = (
        (YOUTUBE_DL, _('youtube-dl')),
    )

    url = models.TextField()
    downloader = models.PositiveSmallIntegerField(choices=DOWNLOADER_CHOICES, null=True)
    celery_id = models.UUIDField(null=True)
    state = models.PositiveSmallIntegerField(choices=STATE_CHOICES, default=QUEUED)
    is_hidden = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)

    release = models.OneToOneField('rls.Release', null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        ordering = ('-created_at', )

    def async_result(self):
        return AsyncResult(str(self.celery_id))

    def as_dict(self) -> dict:
        result = {
            'url': self.url,
            'id': self.id,
            'state': self.state,
            'requested_by': self.created_by.username,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'finished_at': self.finished_at
        }

        if self.state in {self.DOWNLOADING, self.PROCESSING, self.ERROR}:
            info = self.async_result().info
            if info:
                result.update({
                    'total': info['total_bytes'],
                    'downloaded': info['downloaded_bytes'],
                    'filename': os.path.basename(info['filename']).split('_', 1)[-1]
                })
            if self.state == self.ERROR:
                # TODO: Continue here: Add task error listing endpoint
                result['errors'] = '' # reverse('rlsget:errors', args=[self.id])
        elif self.state == self.FINISHED:
            release = self.release

            result.update({
                'name': release.name,
                'details': reverse('rls:details', args=[release.id])
            })
        return result


class TaskTraceback(models.Model):
    download_task = models.ForeignKey(DownloadTask, related_name='tracebacks')

    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
