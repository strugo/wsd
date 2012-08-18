# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext


def index(request):
    data = {}
    return render_to_response("core/index.html", data, context_instance=RequestContext(request))
