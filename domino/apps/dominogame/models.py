# -*- coding: utf-8 -*-

import hashlib
import datetime
import json

from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings


CHIP_VALUES = (
    (0, 'empty'),
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
)

CHIP_ANGLES = (
    (0, '0'), # left | right
    (1, '90'), # clock wise
    (2, '180'),
    (3, '270'),
)


class GameRoom(models.Model):
    '''
    Game room model
    '''
    is_active = models.BooleanField(_(u'Active'), default=False, db_index=True)
    comet_id  = models.CharField(_(u'Comet id'), max_length=32, default='', blank=True)
    created = models.DateTimeField(_(u'Created'), auto_now_add=True, db_index=True)
    is_closed = models.BooleanField(_(u'Close for join'), default=False)
    is_finished = models.BooleanField(_(u'Game finished'), default=False)


    class Meta:
        verbose_name = _(u'room')
        verbose_name_plural = _(u'Game rooms')


    def __unicode__(self):
        return u'%s' % self.created

    def __int__(self):
        return self.pk


    def get_absolute_url(self):
        return reverse('domino_game_room', args=[self.pk, ])


    @classmethod
    def create_game(cls):
        '''
        Create new game room:
        1. Create GameRoom object
        2. Create chips
        return GameRoom object
        '''
        room = cls.objects.create()
        hash_str = u'%s+%s+%s' % (
            str(datetime.datetime.now()),
            settings.SECRET_KEY,
            room.id,
        )
        room.comet_id = hashlib.md5(hash_str).hexdigest()
        room.save()
        for left in CHIP_VALUES:
            for right in CHIP_VALUES:
                data = {
                    'room': room,
                    'left': left[0],
                    'right': right[0],
                }
                GameChip.objects.create(**data)
        return room


    def get_chip(self):
        '''
        Return new chip from bank
        If there is no chips - return None
        '''
        try:
            return self.room_chips.all().filter(used=False)[0]
        except IndexError:
            return None


    def get_random_chip(self):
        '''
        Return new random chip from bank
        If there is no chips - return None
        '''
        try:
            return self.room_chips.all().filter(used=False).order_by('?')[0]
        except IndexError:
            return None


    def join_member(self, user):
        '''
        Get user and return game member.
        Create member if him not exist and chip gives.
        '''
        try:
            member = GameMember.objects.filter(room=self, user=user)[0]
        except IndexError:
            member = GameMember.objects.create(room=self, user=user)
            for i in xrange(5):
                chip = self.get_random_chip()
                if chip:
                    chip.used = True
                    chip.save()
                    member.chips.add(chip)
            member.save()
        return member


    def get_member(self, user):
        '''
        Return game member by user or None
        '''
        try:
            return self.room_members.filter(user=user)[0]
        except IndexError:
            return None


    def to_JSON(self, user=None):
        members = []
        for m in self.room_members.all():
            members.append({
                'username': m.user.username,
                'chips_count': m.chips.count(),
            })

        game = []

        my_chips = []
        if user:
            try:
                member = GameMember.objects.filter(room=self, user=user)[0]
            except IndexError:
                pass
            else:
                for c in member.chips.all():
                    my_chips.append({
                        'id': c.id,
                        'left': c.left,
                        'right': c.right,
                    })

        data = {
            'members': members,
            'game': game,
            'my_chips': my_chips,
        }

        return json.dumps(data)


class GameChip(models.Model):
    '''
    Chips
    '''
    room = models.ForeignKey(GameRoom, verbose_name=_(u'Game room'), db_index=True, related_name='room_chips')
    left = models.IntegerField(_(u"Left value"), choices=CHIP_VALUES, db_index=True)
    right = models.IntegerField(_(u"Right value"), choices=CHIP_VALUES, db_index=True)
    angle = models.IntegerField(_(u'Angle'), default=0, choices=CHIP_ANGLES, db_index=True)
    prev = models.ForeignKey('self', verbose_name=_(u'Previous chip'), null=True, blank=True, db_index=True)
    used = models.BooleanField(_(u'Used chip'), default=False, db_index=True)


    class Meta:
        verbose_name = _(u'chip')
        verbose_name_plural = _(u'Chips')
        ordering = ['pk',]


    def __int__(self):
        return self.pk

    def __unicode__(self):
        return '%i|%i' % (self.left, self.right,)


class GameMember(models.Model):
    '''
    Game members
    '''
    room = models.ForeignKey(GameRoom, verbose_name=_(u'Game room'), db_index=True, related_name='room_members')
    user = models.ForeignKey(User, verbose_name=_(u'User'), db_index=True)
    chips = models.ManyToManyField(GameChip, verbose_name=_(u'Chips'), blank=True, null=True, related_name='users_chips')


    class Meta:
        verbose_name = _(u'game member')
        verbose_name_plural = _(u'Game members')
        ordering = ['pk',]

    def __unicode__(self):
        return self.user.username

