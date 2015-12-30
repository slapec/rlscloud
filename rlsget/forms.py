# coding: utf-8

from django import forms
from django.db import transaction

from rlsget.tasks import youtube_dl
from rlsget.models import DownloadTask


class DownloadTaskForm(forms.ModelForm):
    class Meta:
        model = DownloadTask
        fields = ('url', )

    def __init__(self, *args, created_by, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.created_by = created_by

    @transaction.atomic
    def save(self, commit=True):
        instance = super().save()
        youtube_dl.apply_async([instance.pk])

        return instance
