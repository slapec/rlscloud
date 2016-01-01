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
        qs = DownloadTask.objects.filter(is_archived=False).prefetch_related('release', 'created_by')
        download_queue = [_.as_dict() for _ in qs]
        return JsonResponse(download_queue, safe=False)

    def post(self, request):
        form = DownloadTaskForm(request.POST, created_by=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({})
        else:
            return JsonResponse(form.errors, status=400)


@method_decorator(login_required, name='dispatch')
class TaskApi(View):
    def patch(self, request, task_id):
        task = get_object_or_404(DownloadTask, pk=task_id, state__in=DownloadTask.ARCHIVABLE_STATES, is_archived=False)
        with transaction.atomic():
            task.is_archived = True
            task.save()
            return JsonResponse({})

    def delete(self, request, task_id):
        task = get_object_or_404(DownloadTask, pk=task_id, state__in=DownloadTask.CANCELABLE_STATES)
        task.cancel()
        return JsonResponse({})


@method_decorator(login_required, name='dispatch')
class TracebackApi(View):
    def get(self, request, task_id):
        task = get_object_or_404(DownloadTask, pk=task_id, state=DownloadTask.ERROR)
        return JsonResponse([_.as_dict() for _ in task.tracebacks.all()], safe=False)
