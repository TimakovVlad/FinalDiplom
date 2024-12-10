"""
Django settings for retail_automation project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
from baton.ai import AIModels
from .my_auth import email_host_user, email_host_password, your_client_id, your_client_secret

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-_1z5$vsq&3#p@o_fj!c&vsz$9f!4a@xyaoqro*z!v8e9foonhh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'users.CustomUser'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # наши приложения
    'users',
    'products',
    'orders',

    # другие приложения
    'django_extensions',
    'drf_spectacular',
    'django_celery_beat',
    'baton',
    'baton.autodiscover',
    'easy_thumbnails',

    # DRF
    'rest_framework',
]

# Настройки для Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',  # Ограничение для авторизованных пользователей
        'rest_framework.throttling.AnonRateThrottle',  # Ограничение для анонимных пользователей
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '5/minute',     # 5 запросов в минуту для авторизованных пользователей
        'anon': '5/minute',     # 1 запрос в минуту для анонимных пользователей
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'retail_automation.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'retail_automation.wsgi.application'


THUMBNAIL_ALIASES = {
    '': {
        'small': {'size': (50, 50), 'crop': True},  # Миниатюра 50x50
        'medium': {'size': (200, 200), 'crop': True},  # Миниатюра 200x200
        'large': {'size': (500, 500), 'crop': True},  # Миниатюра 500x500
    },
}


BATON = {
    'SITE_HEADER': 'Baton',
    'SITE_TITLE': 'Baton',
    'INDEX_TITLE': 'Site administration',
    'SUPPORT_HREF': 'https://github.com/otto-torino/django-baton/issues',
    'COPYRIGHT': 'copyright © 2020 <a href="https://www.otto.to.it">Otto srl</a>', # noqa
    'POWERED_BY': '<a href="https://www.otto.to.it">Otto srl</a>',
    'CONFIRM_UNSAVED_CHANGES': True,
    'SHOW_MULTIPART_UPLOADING': True,
    'ENABLE_IMAGES_PREVIEW': True,
    'CHANGELIST_FILTERS_IN_MODAL': True,
    'CHANGELIST_FILTERS_ALWAYS_OPEN': False,
    'CHANGELIST_FILTERS_FORM': True,
    'CHANGEFORM_FIXED_SUBMIT_ROW': True,
    'MENU_ALWAYS_COLLAPSED': False,
    'MENU_TITLE': 'Menu',
    'MESSAGES_TOASTS': False,
    'GRAVATAR_DEFAULT_IMG': 'retro',
    'GRAVATAR_ENABLED': True,
    'LOGIN_SPLASH': '/static/core/img/login-splash.png',
    'FORCE_THEME': None,
    'SEARCH_FIELD': {
        'label': 'Search contents...',
        'url': '/search/',
    },
    'BATON_CLIENT_ID': 'xxxxxxxxxxxxxxxxxxxx',
    'BATON_CLIENT_SECRET': 'xxxxxxxxxxxxxxxxxx',
    'AI': {
        "MODELS": "myapp.foo.bar", # alternative to the below for lines, a function which returns the models dictionary
        "IMAGES_MODEL": AIModels.BATON_DALL_E_3,
        "VISION_MODEL": AIModels.BATON_GPT_4O_MINI,
        "SUMMARIZATIONS_MODEL": AIModels.BATON_GPT_4O_MINI,
        "TRANSLATIONS_MODEL": AIModels.BATON_GPT_4O,
        'ENABLE_TRANSLATIONS': True,
        'ENABLE_CORRECTIONS': True,
        'CORRECTION_SELECTORS': ["textarea", "input[type=text]:not(.vDateField):not([name=username]):not([name*=subject_location])"],
        "CORRECTIONS_MODEL": AIModels.BATON_GPT_3_5_TURBO,
    },
    'MENU': (
        { 'type': 'title', 'label': 'main', 'apps': ('auth', ) },
        {
            'type': 'app',
            'name': 'auth',
            'label': 'Authentication',
            'icon': 'fa fa-lock',
            'models': (
                {
                    'name': 'user',
                    'label': 'Users'
                },
                {
                    'name': 'group',
                    'label': 'Groups'
                },
            )
        },
        { 'type': 'title', 'label': 'Contents', 'apps': ('flatpages', ) },
        { 'type': 'model', 'label': 'Pages', 'name': 'flatpage', 'app': 'flatpages' },
        { 'type': 'free', 'label': 'Custom Link', 'url': 'http://www.google.it', 'perms': ('flatpages.add_flatpage', 'auth.change_user') },
        { 'type': 'free', 'label': 'My parent voice', 'default_open': True, 'children': [
            { 'type': 'model', 'label': 'A Model', 'name': 'mymodelname', 'app': 'myapp' },
            { 'type': 'free', 'label': 'Another custom link', 'url': 'http://www.google.it' },
        ] },
    )
}


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Результаты задач
CELERY_RESULT_BACKEND = 'django-db'

# Таймзона для задач
CELERY_TIMEZONE = 'UTC'

# Настройка сохранения результатов
INSTALLED_APPS += [
    'django_celery_results',
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # Real
# EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend' # Test
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = email_host_user  # Ваш email
EMAIL_HOST_PASSWORD = email_host_password  # Пароль от email (добавьте их в файл my_auth.py)

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',  # Оставляем базовый бэкенд для стандартной аутентификации
)

# Конфигурация для Google
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = your_client_id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = your_client_secret #(добавьте их в файл my_auth.py)


# Настройки для редиректа после успешной аутентификации
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
