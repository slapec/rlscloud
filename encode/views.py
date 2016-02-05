# coding: utf-8

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import View

from rls.models import Release
from encode.tasks import encode


@method_decorator(login_required, name='dispatch')
class Request(View):
    def get(self, request, rls_id):
        release = get_object_or_404(Release, pk=rls_id)
        encode.apply_async([release.file.url])

        return JsonResponse({})
