# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from datetime import datetime, timedelta
#from .settings import *
from uuid import uuid4
from django.core.urlresolvers import reverse


class UserProfile(models.Model):
    '''
    Base user profile
    '''
    user = models.ForeignKey(User, verbose_name=_(u"User"), db_index=True, related_name='user_profile')
    played = models.IntegerField(_(u"Games played"), default=0, db_index=True)
    wined = models.IntegerField(_(u"Games wined"), default=0, db_index=True)

    class Meta:
        verbose_name = u"profile"
        verbose_name_plural = u"Profiles"

    def __unicode__(self):
        return self.user.username


def autocreate_profile(sender, **kwargs):
    '''
    Autocreate user profile
    '''
    instance = kwargs.get('instance', None)
    created = kwargs.get('created', False)
    if created and instance is not None:
        UserProfile.objects.create(user=instance)

post_save.connect(autocreate_profile, User)


###############################################################################
class AQManager(models.Manager):
    '''
    Queue
    '''
    def create_queue(self, user=None):
        '''
        Создать очередь активации.
        '''
        if user is None:
            return
        uuid = str(uuid4())
        return self.create(user=user, uuid=uuid)


class PasswordRestoreQueue(models.Model):
    '''
    Password resotore
    '''
    user = models.ForeignKey(User, verbose_name=_(u"User"), db_index=True)
    uuid = models.CharField(_(u"UUID"), max_length=64, blank=False)
    date = models.DateTimeField(_(u"Datetime"), auto_now_add=True)

    objects = AQManager()

    class Meta:
        verbose_name = _(u"password restore queue")
        verbose_name_plural = _(u"Password resotre")

    def __unicode__(self):
        return self.uuid

    def is_active(self):
        if (datetime.now() - self.date) < timedelta(days=3):
            return True
        return False

    def get_absolute_url(self):
        return reverse('reset_password_page', args=[self.uuid, ])




