"""
Django settings for store project.
Mahashankh — Wallpaper & Home Decor E-commerce
"""

import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env file
env = environ.Env(
    DJANGO_DEBUG=(bool, True),
    DJANGO_ALLOWED_HOSTS=(str, '*'),
)
_env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(_env_path):
    environ.Env.read_env(_env_path)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-fallback-key-change-me')

DEBUG = env('DJANGO_DEBUG')

ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS').split(',')

# Allow Vercel deployment URLs (e.g. wallpaper-xxx.vercel.app)
_vercel_url = os.environ.get('VERCEL_URL')
if _vercel_url:
    ALLOWED_HOSTS.append(_vercel_url)
    ALLOWED_HOSTS.append(f'.{_vercel_url}')

# Login URL — @login_required redirects here
LOGIN_URL = '/login/'

# CSRF trusted origins — allows HTTPS POST requests through Caddy proxy
CSRF_TRUSTED_ORIGINS = [
    'https://*.drytis.dev',
    'http://*.drytis.dev',
    'https://*.vercel.app',
    'http://*.vercel.app',
]

# Trust the proxy so Django knows the original scheme was HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'store.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop.context_processors.cart_count',
                'shop.context_processors.categories',
                'shop.context_processors.notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'store.wsgi.application'

# Database — PostgreSQL (local) or Neon (production via DATABASE_URL)
import dj_database_url

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Production / Neon — parse the connection URL and enforce SSL
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', os.environ.get('DB_NAME', 'redwine_db')),
            'USER': os.environ.get('POSTGRES_USER', os.environ.get('DB_USER', 'redwine')),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', os.environ.get('DB_PASSWORD', 'redwine2026')),
            'HOST': os.environ.get('POSTGRES_HOST', os.environ.get('DB_HOST', '127.0.0.1')),
            'PORT': os.environ.get('POSTGRES_PORT', os.environ.get('DB_PORT', '5432')),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Whitenoise: serve static files in production through gunicorn
STORAGES = {
    'default': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@mahashank.com'

# Razorpay
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')
RAZORPAY_CURRENCY = 'INR'

# Demo mode is active when no Razorpay credentials are configured.
# This lets the full payment flow be tested without a real gateway account.
RAZORPAY_DEMO_MODE = not (RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET)
