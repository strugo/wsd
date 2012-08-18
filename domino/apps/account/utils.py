# -*- coding: utf-8 -*-

from django.core.mail import  mail_managers, EmailMultiAlternatives
from django.template import loader
from django.conf import settings
from django.template import Context
#from .cmscore.context_processors import load_cms_vars
from django.utils.html import strip_tags


DEFAULT_FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL', 'root@localhost')

__all__ = ('send_email', 'send_manager_email', 'send_unregistered_email',)


def send_email(request, user, subject, template, attrs={}):
    a = {}
    a.update(attrs)
    #a.update(load_cms_vars(request))
    t = loader.get_template(template)
    body = t.render(Context(a))
    body_clean = strip_tags(body)
    email = user.email
    msg = EmailMultiAlternatives(subject, body_clean, DEFAULT_FROM_EMAIL, (email,))
    msg.attach_alternative(body, "text/html")
    msg.send(fail_silently=True)


def send_manager_email(request, subject, template, attrs={}):
    a = {}
    a.update(attrs)
    #a.update(load_cms_vars(request))
    t = loader.get_template(template)
    body = t.render(Context(a))
    body_clean = strip_tags(body)
    mail_managers(subject, body_clean, fail_silently=False, html_message=body)


def send_unregister_email(request, email, subject, template, attrs={}):
    a = {}
    a.update(attrs)
    #a.update(load_cms_vars(request))
    t = loader.get_template(template)
    body = t.render(Context(a))
    body_clean = strip_tags(body)
    msg = EmailMultiAlternatives(subject, body_clean, DEFAULT_FROM_EMAIL, (email,))
    msg.attach_alternative(body, "text/html")
    msg.send(fail_silently=True)
