# coding: utf-8

from django.conf.urls import url

from encode.views import Request

urlpatterns = [
    url(r'^(?P<rls_id>\d+)/$', view=Request.as_view(), name='request'),
]
