# coding: utf-8

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, View

from rlsget.forms import DownloadTaskForm
from rlsget.models import DownloadTask


@method_decorator(login_required, name='dispatch')
class QueueView(TemplateView):
    template_name = 'rlsget/queue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'rlscloud_urls': {
                'queue_api': reverse('rlsget:queue-api')
            },
            'rlscloud_options': {
                'states': {k: str(v) for k, v in DownloadTask.STATE_CHOICES},
                'i18n': {'na': _('N/A')}
            }
        })
        return context


@method_decorator(login_required, name='dispatch')
class QueueApi(View):
    def get(self, request):
        qs = DownloadTask.objects.filter(is_hidden=False).prefetch_related('release', 'created_by')
        download_queue = [_.as_dict() for _ in qs]
        return JsonResponse(download_queue, safe=False)

    def post(self, request):
        form = DownloadTaskForm(request.POST, created_by=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({})
        else:
            return JsonResponse(form.errors, status=400)

    def patch(self, request):
        download_task = get_object_or_404(DownloadTask, pk=request.POST['id'], is_hidden=False)
        with transaction.atomic():
            download_task.is_hidden = True
            download_task.save()
            return JsonResponse({})

    def delete(self, request):
        # TODO: Continue here: implement task cancellation
        print(request.POST)
