# coding: utf-8

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from rlsget.models import DownloadTask
from rls.tasks import create_thumbnails


class Release(models.Model):
    name = models.CharField(max_length=256)
    file = models.FileField(upload_to=settings.RELEASE_DIR)
    file_hash = models.CharField(max_length=32)
    thumbnail = models.ImageField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        ordering = ('-created_at', )


@receiver(post_save, sender=Release)
def thumbnails_for_new_release(sender, **kwargs):
    if kwargs['created']:
        create_thumbnails.apply_async([kwargs['instance'].pk])
