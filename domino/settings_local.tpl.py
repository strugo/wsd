# -*- coding: utf-8 -*-
###############################################################################
###
### Local project settings
###
###############################################################################
import os
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Leonid Nasedkin', 'leonidnasedkin@gmail.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        }
}


MEDIA_ROOT = os.path.join(PROJECT_PATH, 'files/media/')
MEDIA_URL = '/media/'
STATIC_ROOT = ''
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'files/static/'),
    )
