"""
Django settings for meetup_bot project.
"""

import datetime as dt
import environ
import sentry_sdk
import logging
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


root = environ.Path(__file__) - 2
env = environ.Env(
    DEBUG=(bool, False),
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',

    'meetup_bot.meetup_bot',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meetup_bot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [root('meetup_bot/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meetup_bot.wsgi.application'


# Database

DATABASES = {
    'default': env.db(),
}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = env('STATIC_URL', default='/static/')

STATIC_ROOT = env('STATIC_ROOT', default=root('static'))

MEDIA_URL = env('MEDIA_URL', default='/media/')

MEDIA_ROOT = env('MEDIA_ROOT', default=root('media'))


# --- Celery

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='')

# Store task results in Redis
CELERY_RESULT_BACKEND = env('CELERY_BROKER_URL', default='')

# Task result life time until they will be deleted
CELERY_RESULT_EXPIRES = int(dt.timedelta(days=1).total_seconds())

# Needed for worker monitoring
CELERY_SEND_EVENTS = True

CELERY_BEAT_SCHEDULE = {}

# default to json serialization only
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


if env('SENTRY_DSN', default=''):
    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR     # Send error events from log messages
    )

    sentry_sdk.init(
        dsn=env('SENTRY_DSN', default=''),
        integrations=[DjangoIntegration(), sentry_logging]
    )

MEETUP_COM_API_TOKEN = env('MEETUP_COM_API_TOKEN', default='')

REPUTATION_SCORE = {
    'yes, attended': 0,  # confirmed went (2019-03-13: doesn't work anymore, now it is 'yes, None'
    'yes, noshow': 1,  # said he will be here, but did not come
    'yes, absent': 0,    # said he will be there, but then the organizer selected 'didn't go' instead of 'noshow' (we have forgiven)

    'no, attended': 0, # said he won't be there, attended anyway
    'no, absent': 0,      # said he will be there, but has canceled in time
    'no, noshow': 1,   # said he will be here, canceled too late, got a penalty

    'yes, None': 0,       # said he will go, but we don't know what happened yet UPDATE 2019-03-13 Meetup messed up their API AGAIN and doesn't output 'attended' anymore, so we land here.
    'no, None': 0,        # decided not to go before the event (did not click anything) or said he won't go and we don't know what happened yet
}
