# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from dominogame.models import GameRoom



def load_game_status(request):
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
    pass


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
    pass


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
    data = {
        'room': room,
        'member': member,
    }
    return render_to_response("dominogame/room_create.html", data, context_instance=RequestContext(request))


@login_required
def join_to_room(request, room_id):
    try:
        room = GameRoom.objects.get(id=room_id)
    except GameRoom.DoesNotExist:
        return redirect(reverse('room_select'))
    if not room.is_closed and not room.is_finished:
        room.join_member(request.user)
        return HttpResponse('Ok')
    else:
        return redirect(reverse('room_select'))
        
