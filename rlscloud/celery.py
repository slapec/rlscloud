# coding: utf-8

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rlscloud.settings')

from django.conf import settings

app = Celery('rlscloud')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
