# coding: utf-8

from celery.result import AsyncResult
from django.utils.translation import ugettext_lazy as _
from django.db import models


class ReleaseDownloadFile(models.Model):
    QUEUED = 0
    DOWNLOADING = 1
    FINISHED = 2
    ERROR = 3

    STATE_CHOICES = (
        (QUEUED, _('Queued')),
        (DOWNLOADING, _('Downloading')),
        (FINISHED, _('Finished')),
        (ERROR, _('Error'))
    )

    source = models.TextField()
    state = models.PositiveSmallIntegerField(choices=STATE_CHOICES, default=QUEUED)
    celery_task = models.UUIDField(null=True, blank=True)
    queue_datetime = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        result = {
            'state': self.state,
            'source': self.source,
            'celery_task': self.celery_task,
            'status': None
        }

        if self.state == self.DOWNLOADING:
            async_result = AsyncResult(str(self.celery_task))
            if async_result.state == 'PROGRESS':
                result['status'] = async_result.info['_percent_str']

        return result