# -*- coding: utf-8 -*-
###############################################################################
###
### Global project settings
###
###############################################################################
import os
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
###############################################################################
import sys
sys.path.append(os.path.join(PROJECT_PATH, 'apps'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Leonid Nasedkin', 'leonidnasedkin@gmail.com'),
)

MANAGERS = ADMINS

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

TIME_ZONE = 'Asia/Novosibirsk'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = os.path.join(PROJECT_PATH, 'files/media/')
MEDIA_URL = '/media/'
STATIC_ROOT = ''
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'files/static/'),
    )

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

SECRET_KEY = 'pn05+x3f!20qem60w!n@85n7-4i+zch_+j@ym@@1kr7$l_v2u+'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )

ROOT_URLCONF = 'domino.urls'

WSGI_APPLICATION = 'domino.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',

    'cmscore.context_processors.load_cms_context',
    )

FIXTURE_DIRS = (
    os.path.join(PROJECT_PATH, 'fixtures')
    )

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates/'),
    )


AUTH_PROFILE_MODULE = 'account.UserProfile'
LOGIN_URL = '/login/'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'south',
    'supercaptcha',
    'cmscore',
    'bootstrap',

    'account',
    'core',
    'dominogame',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(PROJECT_PATH, 'cache/'),
        },
    }

### CMS context
PROJECT_TITLE = u"Domino"


###############################################################################

try:
    from settings_local import *
except ImportError:
    pass
