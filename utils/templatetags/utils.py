# coding: utf-8

import json

from django import template

register = template.Library()


@register.filter(name='json')
def json_filter(value):
    if not value:
        value = {}
    return json.dumps(value)
