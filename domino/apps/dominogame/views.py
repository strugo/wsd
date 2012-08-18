# -*- coding: utf-8 -*-

import datetime
import json

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from dominogame.models import GameRoom, GameMember

import stomp


def load_game_status(request, room_id):
    '''
    Return game status
    {
        'users': {
            1: (username, chips_counter),
            2: ...,
            3: ...,
        },
        'game': {
            1: (chip_id, left, right, angle),
            2: ...,
            n: ...
        },
        'my_chips': {
            1: (id, left, right),
            2: ...,
            n: ...
        }
    }
    '''
    try:
        room = GameRoom.objects.get(id=room_id)
    except GameRoom.DoesNotExist:
        raise Http404
    return HttpResponse(room.to_JSON(request.user))


def game_comet_chanel(request):
    '''
    Send events via comet:
    1. game_step:
        (user, chip_id, left, right, angle)
    2. users_change:
        (user, chip_count)
    3. Chat:
        (user, message)
    4. Start game:
        (start)
    5. End game
    6. Disconnect user
    '''
    conn = stomp.Connection()
    conn.start()
    conn.connect()
    conn.subscribe(destination='/%s' % room.comet_id, ack='auto')

    msg_to_send = room.to_JSON(request.user)
    conn.send(msg_to_send, destination='/%s' % room.comet_id)


def get_new_chip(request):
    '''
    Return new chip from bank
    (chip_id, left, right)
    also create new comet event user_change
    '''
    pass


@login_required
def room_select(request):
    open_room_list = GameRoom.objects.filter(is_closed=False, is_finished=False)
    data = {
        'open_room_list': open_room_list,
    }
    return render_to_response("dominogame/room_select.html", data, context_instance=RequestContext(request))


@login_required
def room_create(request):
    room = GameRoom.create_game()
    member = room.join_member(request.user)
    return redirect(reverse('room', args=[room.id]))


@login_required
def join_to_room(request, room_id):
    try:
        room = GameRoom.objects.get(id=room_id)
    except GameRoom.DoesNotExist:
        return redirect(reverse('room_select'))
    if not room.is_closed and not room.is_finished:
        room.join_member(request.user)
        return redirect(reverse('room', args=[room.id]))
    else:
        return redirect(reverse('room_select'))


@login_required
def room(request, room_id):
    try:
        room = GameRoom.objects.get(id=room_id)
    except GameRoom.DoesNotExist:
        return redirect(reverse('room_select'))

    #get me as member
    try:
        member = GameMember.objects.filter(room=room, user=request.user)[0]
    except IndexError:
        member = None

    data = {
        'room': room,
        'member': member,
    }
    return render_to_response("dominogame/room.html", data, context_instance=RequestContext(request))


def step(request, room_id):
    try:
        room = GameRoom.objects.get(id=room_id)
    except GameRoom.DoesNotExist:
        pass
    else:
        conn = stomp.Connection()
        conn.start()
        conn.connect()
        conn.subscribe(destination='/%s' % room.comet_id, ack='auto')
        time = datetime.datetime.now()
        msg_to_send = json.dumps({"time":time.strftime("%H:%S-%d/%m/%Y")})
        conn.send(msg_to_send)
    return HttpResponse("ok")

