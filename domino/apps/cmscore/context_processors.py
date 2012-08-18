# -*- coding: utf-8 -*-
from django.conf import settings

def load_cms_context(request):
    return {
        'PROJECT_TITLE': getattr(settings, 'PROJECT_TITLE', 'Django project'),
        'STATIC_URL': getattr(settings, 'STATIC_URL', '/static/'),
        'MEDIA_URL': getattr(settings, 'MEDIA_URL', '/media/'),
        'DOMAIN': getattr(settings, 'DOMAIN', 'localhost'),
        'ORBITED': getattr(settings, 'ORBITED'),
        'STOMP': getattr(settings, 'STOMP'),
    }
  
