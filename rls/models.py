# coding: utf-8

from django.conf import settings
from django.db import models

from rlsget.models import DownloadTask


class Release(models.Model):
    title = models.CharField(max_length=256)
    file = models.FileField(upload_to=settings.RELEASE_DIRECTORY)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
