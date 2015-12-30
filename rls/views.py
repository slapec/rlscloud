# coding: utf-8

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from rls.models import Release


@method_decorator(login_required, name='dispatch')
class Latest(TemplateView):
    template_name = 'rls/latest.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'rlscloud_options': {
                'active': 'rls-latest',
            },
            'releases': Release.objects.all(),
        })
        return context


@method_decorator(login_required, name='dispatch')
class Details(TemplateView):
    template_name = 'rls/details.html'

    def get_context_data(self, **kwargs):
        rls_id = kwargs['rls_id']

        release = get_object_or_404(Release, id=rls_id)
        context = super().get_context_data(**kwargs)

        context['release'] = release

        return context