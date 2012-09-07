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
    members = GameMember.objects.filter(user=request.user)
    my_open_games = GameRoom.objects \
        .filter(room_members__in=members, is_finished=False)
    data = {
        'open_room_list': open_room_list,
        'my_open_games': my_open_games,
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
        raise Http404()
    else:
        turn_member = room.get_turn_member()
        if room.is_active and not turn_member.user == request.user:
            return HttpResponse("fail")

        action = request.POST.get('action')
        if action == 'game_start':
            room.game_start()
        elif action == 'get_chip':
            member = room.get_member(request.user)
            random_chip = room.get_random_chip()
            random_chip.used = True
            random_chip.save()
            member.chips.add(random_chip)
            member.save()

            chips_in_bank = room.room_chips.filter(used=False).count()

            extra = {
                'status': 'ok',
                'chips_in_bank': chips_in_bank,
            }
            return HttpResponse(random_chip.to_JSON(extra=extra))

        elif action == 'process_turn':
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
                    try:
                        table_id = int(request.POST.get('table_id'))
                        chip_prev = room.room_chips.filter(id=table_id)[0]
                    except (ValueError, TypeError, IndexError):
                        pass
                    else:
                        if not chip_prev.is_border_mark:
                            return HttpResponse("fail")
                        chip.prev = chip_prev


                    if not room.can_next(chip):
                        return HttpResponse("fail")

                    if chip_prev and len(room.get_tree_chips()) > 2:
                        chip_prev.is_border_mark = False
                        chip_prev.save()

                    chip.on_table = True
                    chip.is_border_mark = True
                    chip.save()

                    room.set_last(chip)

                    turn_member = room.get_turn_member()
                    if turn_member:
                        turn_user_id = turn_member.user.id
                    else:
                        turn_user_id = None

                    chips_in_bank = room.room_chips.filter(used=False).count()
                    print chips_in_bank

                    extra = {
                        'action':'place_chip',
                        'turn_user_id': turn_user_id,
                        'chips_in_bank': chips_in_bank,
                    }
                    msg_to_send = chip.to_JSON(extra=extra)

            room.send_message(msg_to_send)

    return HttpResponse(json.dumps({'status': 'ok'}))


@login_required
def chat_message(request, room_id):
    try:
        room = GameRoom.objects.get(id=room_id)
    except GameRoom.DoesNotExist:
        raise Http404()

    if not room.room_members.all().filter(user=request.user):
        raise Http404()

    message = request.POST.get('message', '')

    if message:
        msg = {
            'action': 'chat_message',
            'username': request.user.username,
            'message': message,
        }
        room.send_message(json.dumps(msg))

    return HttpResponse(json.dumps({'status': 'ok'}))
