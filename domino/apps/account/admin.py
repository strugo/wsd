# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile


class UserProfileAdmin(admin.StackedInline):
    model = UserProfile

class UserAdmin2(UserAdmin):

    list_display = ['id', 'username','email','date_joined','last_login']
    list_display_links = ['username',]
    fieldsets = (
        ( None, { 'fields': ('username','password') } ),
        (u"Имя", { 'fields': ('first_name','last_name', 'email'), } ),
        (u'Статус', { 'fields': ('is_superuser', 'is_staff', 'is_active') } ),
        (u'Даты', { 'fields': ( 'date_joined', 'last_login' ) } ),
        )

    inlines = [
        UserProfileAdmin,
    ]


admin.site.unregister(User)
admin.site.register(User, UserAdmin2)
