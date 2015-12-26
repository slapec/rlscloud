# coding: utf-8

import requests
from django import forms
from django.conf import settings
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from requests.exceptions import MissingSchema, ConnectionError

from rlsget.tasks import youtube_dl
from rlsget.models import DownloadTask


class DownloadTaskForm(forms.ModelForm):
    class Meta:
        model = DownloadTask
        fields = ('url', )

    def __init__(self, *args, created_by, **kwargs):
        super(DownloadTaskForm, self).__init__(*args, **kwargs)
        self.instance.created_by = created_by

    @transaction.atomic
    def save(self, commit=True):
        instance = super(DownloadTaskForm, self).save()
        youtube_dl.apply_async([instance.pk])

        return instance
