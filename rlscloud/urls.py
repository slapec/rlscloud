# coding: utf-8

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', view=RedirectView.as_view(url=reverse_lazy('rls:latest')), name='index'),

    url(r'^rlsget/', include('rlsget.urls', namespace='rlsget')),
    url(r'^rls/', include('rls.urls', namespace='rls')),
    url(r'^accounts/login/$', auth_views.login, name='login'),
    # url(r'^admin/', include(admin.site.urls)),
]
