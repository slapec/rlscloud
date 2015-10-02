# coding: utf-8

from django.conf.urls import url

from rlsget.views import queue, queue_json, enqueue

urlpatterns = [
    url(r'^queue/$', view=queue, name='queue'),
    url(r'^enqueue/$', view=enqueue, name='enqueue'),
    url(r'^queue_json/$', view=queue_json, name='queue_json')
]
