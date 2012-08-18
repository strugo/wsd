# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('dominogame.views',
    url(r'^room/(\d+)/$', 'room', name="room"),
    url(r'^room_select/$', 'room_select', name="room_select"),
    url(r'^room_create/$', 'room_create', name="room_create"),
    url(r'^join_to_room/(\d+)/$', 'join_to_room', name="join_to_room"),
)

