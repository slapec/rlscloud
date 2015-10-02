# coding: utf-8

from django.db import models


class Release(models.Model):
    title = models.CharField(max_length=128)
    date = models.DateField()
