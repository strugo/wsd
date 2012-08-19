# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from dominogame.models import GameRoom, GameMember


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


def game_step(request, room_id):
    msg_to_send = ''
    try:
        room = GameRoom.objects.get(id=room_id)
    except GameRoom.DoesNotExist:
        pass
    else:
        if not room.get_turn_member().user == request.user:
            return HttpResponse("fail")

        action = request.POST.get('action')
        if action == 'game_start':
            extra = {
                'action':'game_start',
            }
            msg_to_send = room.to_JSON(user=request.user, extra=extra)
        else:
            try:
                chip_id = int(request.POST.get('chip_id'))
            except (ValueError, TypeError):
                pass
            else:
                member = room.get_member(request.user)
                try:
                    chip = member.chips.filter(id=chip_id)[0]
                except IndexError:
                    pass
                else:
                    if not room.can_next(chip):
                        return HttpResponse("fail")

                    chip.on_table = True
                    chip.is_border_mark = True
                    chip.save()

                    room_json = room.to_JSON()
                    msg_to_send = json.dumps({
                        'room': room_json,
                        'chip': {
                            'chip_id': chip.id,
                            'left': chip.left,
                            'right': chip.right,
                        },
                    })

        room.send_message(msg_to_send)
    return HttpResponse("ok")

