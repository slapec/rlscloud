# coding: utf-8

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View

from rlsget.forms import DownloadTaskForm
from rlsget.models import DownloadTask


@method_decorator(login_required, name='dispatch')
class QueueView(TemplateView):
    template_name = 'rlsget/queue.html'

    def get_context_data(self, **kwargs):
        context = super(QueueView, self).get_context_data(**kwargs)
        context.update({
            'rlscloud_urls': {
                'queue_api': reverse('rlsget:queue-api')
            },
            'rlscloud_options': {
                'active': 'rlsget-queue',
                'states': {k: str(v) for k, v in DownloadTask.STATE_CHOICES}
            }
        })
        return context


@method_decorator(login_required, name='dispatch')
class QueueApi(View):
    def get(self, request):
        download_queue = [_.as_dict() for _ in DownloadTask.objects.all().prefetch_related('release')]
        return JsonResponse(download_queue, safe=False)

    def post(self, request):
        form = DownloadTaskForm(request.POST, created_by=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({})
        else:
            return JsonResponse(form.errors, status=400)
