# coding: utf-8

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View

from rls.forms import ReleaseUploadForm
from rls.models import Release


@method_decorator(login_required, name='dispatch')
class Latest(TemplateView):
    template_name = 'rls/latest.html'

    def get_context_data(self, **kwargs):
        thumbnail_width, thumbnail_height = settings.THUMBNAIL_SIZE

        context = super().get_context_data(**kwargs)
        context.update({
            'rlscloud_options': {
                'active': 'rls-latest'
            },
            'releases': Release.objects.all(),
            'thumbnail_count': settings.THUMBNAIL_COUNT,
            'thumbnail_width': thumbnail_width,
            'thumbnail_height': thumbnail_height
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
        form = ReleaseUploadForm(request.POST, request.FILES, created_by=request.user)

        if form.is_valid():
            form.save()
            return JsonResponse({
                'url': reverse('rls:details', args=[form.instance.pk])
            })
        else:
            return JsonResponse(form.errors, status=400)
