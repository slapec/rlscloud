# coding: utf-8

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View

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


@method_decorator(login_required, name='dispatch')
class Upload(View):
    def get(self, request):
        ctx = {
            'rlscloud_options': {
                'csrf_token': get_token(request)
            },
            'rlscloud_urls': {
                'upload': reverse('rls:upload')
            }
        }
        return render(request, 'rls/upload.html', ctx)

    def post(self, request):
        print(request.FILES['file'].temporary_file_path())

        return JsonResponse({})
