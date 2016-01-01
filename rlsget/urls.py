# coding: utf-8

from django.conf.urls import url

from rlsget.views import QueueView, QueueApi, TaskApi, TracebackApi


urlpatterns = [
    url(r'^$', view=QueueView.as_view(), name='queue-list'),
    url(r'^queue/$', view=QueueApi.as_view(), name='queue-api'),
    url(r'^queue/(?P<task_id>\d+)/$', view=TaskApi.as_view(), name='task-api'),
    url(r'^queue/(?P<task_id>\d+)/errors/$', view=TracebackApi.as_view(), name='traceback-api')
]
