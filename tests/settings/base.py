# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = True

SECRET_KEY = 'NOTASECRET'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dev-database.sqlite3',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'testapp',
    'gargoyle',
    'nexus',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = '/static/'

GARGOYLE_SWITCH_DEFAULTS = {
    'active_by_default': {
        'is_active': True,
        'label': 'Default Active',
        'description': 'When you want the newness',
    },
    'inactive_by_default': {
        'is_active': False,
        'label': 'Default Inactive',
        'description': 'Controls the funkiness.',
    },
}
