# coding: utf-8

import os

from django import forms

from rls.models import Release
from rls.utils import hash_file


class ReleaseUploadForm(forms.ModelForm):
    class Meta:
        model = Release
        fields = ('file', )

    def __init__(self, *args, created_by, **kwargs):
        super().__init__(*args, **kwargs)

        self.instance.created_by = created_by
        self._file_name_original = None

    def clean_file(self):
        file = self.cleaned_data['file']
        self._file_name_original = file.name

        hash_ = hash_file(file.temporary_file_path())
        self.cleaned_data['file_hash'] = hash_
        file.name = hash_ + os.path.splitext(file.name)[-1]

        return file

    def save(self, commit=True):
        self.instance.file_hash = self.cleaned_data['file_hash']
        self.instance.name = os.path.splitext(self._file_name_original)[0]

        return super().save(commit=commit)
