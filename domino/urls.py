# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('core.urls')),
    url(r'^', include('account.urls')),
    url(r'game/', include('dominogame.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^captcha/(?P<code>[\da-f]{32})/$', 'supercaptcha.draw')
)

if settings.DEBUG:
    urlpatterns = patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'', include('django.contrib.staticfiles.urls')),
    ) + urlpatterns
