"""
Django settings for the NSTU E-Medical project.

Everything secret or environment-specific is read from environment variables, so the same
file works on your laptop (sensible defaults) and on a server like Render.

    SECRET_KEY            random string (required in production)
    DEBUG                 "True" locally, "False" in production
    ALLOWED_HOSTS         comma separated host names, e.g. "nstu-emedical.onrender.com"
    EMAIL_HOST_USER       Gmail address used by the contact form (optional)
    EMAIL_HOST_PASSWORD   Gmail *app password* for that address (optional)
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')


def env_bool(name, default):
    return os.environ.get(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


# --- Security -------------------------------------------------------------
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-insecure-key-change-me')
DEBUG = env_bool('DEBUG', True)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
ALLOWED_HOSTS += [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]
if os.environ.get('RENDER_EXTERNAL_HOSTNAME'):  # set automatically by Render
    ALLOWED_HOSTS.append(os.environ['RENDER_EXTERNAL_HOSTNAME'])
CSRF_TRUSTED_ORIGINS = [f'https://{h}' for h in ALLOWED_HOSTS if h not in ('localhost', '127.0.0.1', '[::1]')]

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# --- Application ----------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hospital',
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # serves CSS/images in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'E-medical.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'hospital.context_processors.em_nav',
            ],
        },
    },
]

WSGI_APPLICATION = 'E-medical.wsgi.application'


# --- Database -------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# Keep the integer id type the existing migrations/database use (Django 6 defaults to BigAutoField).
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- Language & time ------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True


# --- Static files & uploads -----------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [STATIC_DIR]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # filled by `collectstatic` on the server
MEDIA_ROOT = os.path.join(BASE_DIR, 'static')         # profile pictures live in static/profile_pic/


# --- Forms, login ---------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

LOGIN_REDIRECT_URL = '/afterlogin'
LOGIN_URL = 'HOME'
LOGOUT_REDIRECT_URL = '/'


# --- Email (contact form, password reset) ---------------------------------
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
else:
    # No mail account configured: print emails to the console instead of failing.
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
