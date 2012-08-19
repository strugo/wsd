# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('account.views',
    url(r'^login/$', 'login_page', name="login_page"),
    url(r'^logout/$', 'logout_page', name="logout_page"),
    url(r'^register/$', 'registration_page', name="registration_page"),
    url(r'^restore/$', 'restore_password', name="password_restore_page"),
    url(r'^restore/(?P<uuid>(\w|-)+)/$', 'reset_password_page', name="reset_password_page"),
    url(r'^settings/$', 'profile_settings', name="profile_settings"),
)
  