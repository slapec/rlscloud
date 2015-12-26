# coding: utf-8

from django.conf.urls import url

from rlsget.views import QueueView, QueueApi


urlpatterns = [
    url(r'^$', view=QueueView.as_view(), name='queue-list'),
    url(r'^queue/$', view=QueueApi.as_view(), name='queue-api')
]
