"""
Django settings for escrutinio_social project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'gq9%*_m)=m*y$cnkl1xeg1xiihaz5%v+_d@a+3ft$b(cq29r8z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'custom_templates',   # our hack to override templates
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'anymail',
    'localflavor',
    'django_extensions',
    'fancy_cache',

    'material.theme.lightblue',
    'material',
    'dbbackup',
    # 'material.admin',
    # 'django.contrib.admin',
    'material.frontend',

    'django_admin_row_actions',
    'hijack',
    'compat',
    # 'attachments',
    'djgeojson',
    'leaflet',
    'versatileimagefield',
    'darkroom',

    # nuestras apps
    'elecciones',
    'fiscales',
    'adjuntos',
    'problemas',
    'contacto'
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

ROOT_URLCONF = 'escrutinio_social.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'elecciones.context_processors.contadores'
            ],
        },
    },
]

WSGI_APPLICATION = 'escrutinio_social.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# Sobreescribir en local_settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db_name',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'db',
        'PORT': '',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = 'America/Argentina/Cordoba'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': os.path.join(BASE_DIR, 'backups')}

HIJACK_LOGIN_REDIRECT_URL = 'home'  # Where admins are redirected to after hijacking a user
HIJACK_ALLOW_GET_REQUESTS = True
HIJACK_LOGOUT_REDIRECT_URL = 'admin:fiscales_fiscal_changelist'


LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (-31.418293, -64.179238),
    'DEFAULT_ZOOM': 8,
    'MIN_ZOOM': 4,
    'MAX_ZOOM': 18,
    'PLUGINS': {
        'awesome-markers': {
            'css': ['https://cdn.rawgit.com/lvoogdt/Leaflet.awesome-markers/2.0/develop/dist/leaflet.awesome-markers.css'],
            'js': 'https://cdn.rawgit.com/lvoogdt/Leaflet.awesome-markers/2.0/develop/dist/leaflet.awesome-markers.min.js',
            'auto-include': True,
        },
    }
}



REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
    ],
    'PAGE_SIZE': 10
}

ANYMAIL = {
    # (exact settings here depend on your ESP...)
    "MAILGUN_API_KEY": "",
    "MAILGUN_SENDER_DOMAIN": '',  # your Mailgun domain, if needepd
}
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"  # or sendgrid.EmailBackend, or...
DEFAULT_FROM_EMAIL = "algo@email.com"         # if you don't already have this in settings
DEFAULT_CEL_CALL = '+54 9 351 XXXXXX'
DEFAULT_CEL_LOCAL = '0351 15 XXXXX'

FULL_SITE_URL = 'https://this-site.com'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        # 'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

# config para el comando importar_actas
IMAPS = [
    {'email': 'e1@gmail.com', 'host': 'imap.gmail.com', 'user': 'e1@gmail.com', 'pass': 'xxxx', 'mailbox': 'INBOX'},
    {'email': 'eml@gmail.com', 'host': 'imap.gmail.com', 'user': 'e2@gmail.com', 'pass': 'xxxx', 'mailbox': 'INBOX'}
]

# contacto settings
CARACTERISTICA_TELEFONO_DEFAULT = '351'     # CORDOBA
CARACTERISTICA_DEFAULT = '351'


# por defecto no se muestra grafico en la página de resultados
SHOW_PLOT = False


try:
    from .local_settings import *
except ImportError:
    pass
