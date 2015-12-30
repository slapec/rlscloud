# coding: utf-8

from django.conf.urls import url

from rls.views import Latest, Details


urlpatterns = [
    url(r'^latest/$', view=Latest.as_view(), name='latest'),
    url(r'^(?P<rls_id>\d+)/$', view=Details.as_view(), name='details')
]
