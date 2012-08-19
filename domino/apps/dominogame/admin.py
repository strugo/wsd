from django.contrib import admin

from models import *


class GameChipInline(admin.TabularInline):
    model = GameChip
    extra = 0
    can_delete = False
    readonly_fields = (
        'id',
        'left',
        'right',
    )
    fields = (
        'id',
        'left',
        'right',
        'angle',
        'prev',
        'used',
        'on_table',
        'is_border_mark',
        'is_last',
    )


class GameRoomAdmin(admin.ModelAdmin):
    inlines = (
        GameChipInline,
    )


class GameMemberAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'room',
    )

admin.site.register(GameRoom, GameRoomAdmin)
admin.site.register(GameChip)
admin.site.register(GameMember)
