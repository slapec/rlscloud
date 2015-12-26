# coding: utf-8

import json

from django.http import HttpResponseBadRequest
from django.utils.encoding import force_text


class JsonInBodyMiddleware:
    def process_request(self, request):
        if request.META['CONTENT_TYPE'].startswith('application/json') and len(request.body) \
                and request.POST.dict() == {}:

            try:
                request.POST = json.loads(force_text(request.body))
            except ValueError:
                return HttpResponseBadRequest('ValueError while parsing request.body')
