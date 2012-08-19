# -*- coding: utf-8 -*-

import hashlib
import datetime
import json

from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings

import stomp


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
            for i in xrange(7):
                chip = self.get_random_chip()
                if chip:
                    chip.used = True
                    chip.save()
                    member.chips.add(chip)
            member.save()
            self.send_message(self.to_JSON(extra={'action':'join_member'}))
        return member


    def get_member(self, user):
        '''
        Return game member by user or None
        '''
        try:
            return self.room_members.filter(user=user)[0]
        except IndexError:
            return None


    def get_all_members(self):
        return self.room_members.all().order_by('id')


    def to_JSON(self, user=None, extra={}):
        members = []
        for m in self.get_all_members():
            members.append({
                'username': m.user.username,
                'id': m.user.pk,
                'chips_count': m.chips.count(),
            })

        log = []
        tree = self.get_tree_chips()
        for c in tree:
            log.append({
                'id': c.id,
                'left': c.left,
                'right': c.right,
                'prev_id': c.prev_id,
            })


        my_chips = []
        if user:
            try:
                member = GameMember.objects.filter(room=self, user=user)[0]
            except IndexError:
                pass
            else:
                for c in member.chips.filter(on_table=False):
                    my_chips.append({
                        'id': c.id,
                        'left': c.left,
                        'right': c.right,
                    })

        turn_member = self.get_turn_member()
        if turn_member:
            turn_user_id = turn_member.user.id
        else:
            turn_user_id = None

        chips_in_bank = self.room_chips.filter(used=False).count()

        data = {
            'members': members,
            'log': log,
            'my_chips': my_chips,
            'turn_user_id': turn_user_id,
            'is_active': self.is_active,
            'chips_in_bank': chips_in_bank,
        }
        data.update(extra)

        return json.dumps(data)


    def table_is_clear(self):
        return self.room_chips.filter(on_table=True).count() == 0


    def can_next(self, chip):
        if self.table_is_clear(): #Table is clear
            turn_chip = self.get_turn_chip()
            print turn_chip
            print chip
            return self.get_turn_chip() == chip


    def get_turn_chip(self):
        members_chips = self.room_chips.filter(used=True)
        first_chip = members_chips.filter(left=1, right=1)
        if first_chip:
            return first_chip[0]
        else:
            for chip in members_chips.all().order_by('left', 'right'):
                if chip.left == chip.right:
                    return chip
        return None


    def get_tree_chips(self):
        try:
            first_chip = self.room_chips \
                .filter(on_table=True, prev__isnull=True)[0]
        except IndexError:
            return []
        tree = []
        chip = first_chip
        while True:
            tree.append(chip)
            try:
                chip = chip.next_chip.get()
            except GameChip.DoesNotExist:
                break
        return tree


    def get_turn_member(self):
        if self.room_members.count() < 2:
            return None

        if self.table_is_clear(): #Table is clear
            chip = self.get_turn_chip()
            if chip:
                return chip.users_chips.get()
            else:
                return None
        else:
            last_turn_member = self.get_tree_chips()[-1].users_chips.get()
            members = self.get_all_members()
            i = 1
            for m in members:
                if m == last_turn_member:
                    if i == len(members):
                        to_return = members[0]
                        return to_return
                    else:
                        to_return = members[i]
                        return to_return
                i+=1


    def game_start(self):
        extra = {
            'action':'game_start',
        }
        #msg_to_send = self.to_JSON(user=request.user, extra=extra)
        #self.send_message(msg_to_send)

        self.is_active = True

        chip = self.get_turn_chip()
        chip.on_table = True
        chip.is_border_mark = True
        chip.save()

        turn_member = self.get_turn_member()
        if turn_member:
            turn_user_id = turn_member.user.id
        else:
            turn_user_id = None

        data = {
            'action':'delete_chip',
            'chip_id':chip.id,
        }
        self.send_message(json.dumps(data))

        extra = {
            'action':'place_chip',
            'turn_user_id': turn_user_id,
        }
        self.send_message(chip.to_JSON(extra=extra))
        self.save()


    def send_message(self, msg):
        conn = stomp.Connection()
        conn.start()
        conn.connect()
        conn.subscribe(destination='/%s' % self.comet_id, ack='auto')
        conn.send(msg, destination='/%s' % self.comet_id)


class GameChip(models.Model):
    '''
    Chips
    '''
    room = models.ForeignKey(GameRoom, verbose_name=_(u'Game room'), db_index=True, related_name='room_chips')
    left = models.IntegerField(_(u"Left value"), choices=CHIP_VALUES, db_index=True)
    right = models.IntegerField(_(u"Right value"), choices=CHIP_VALUES, db_index=True)
    angle = models.IntegerField(_(u'Angle'), default=0, choices=CHIP_ANGLES, db_index=True)
    prev = models.ForeignKey('self', verbose_name=_(u'Previous chip'), null=True, blank=True, db_index=True, related_name='next_chip')
    used = models.BooleanField(_(u'Used chip'), default=False, db_index=True)
    on_table = models.BooleanField(_(u'Chip on table'), default=False, db_index=True)
    is_border_mark = models.BooleanField(_(u'Is border mark'), default=False)


    class Meta:
        verbose_name = _(u'chip')
        verbose_name_plural = _(u'Chips')
        ordering = ['pk',]


    def __int__(self):
        return self.pk

    def __unicode__(self):
        return '%i|%i' % (self.left, self.right,)

    def to_JSON(self, extra={}):
        if self.prev:
            prev_id = self.prev.id
        else:
            prev_id = None

        data = {
            'id' : self.id,
            'left' : self.left,
            'right' : self.right,
            'prev_id': prev_id,
        }
        data.update(extra)
        return json.dumps(data)


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

