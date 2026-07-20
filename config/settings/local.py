"""
Local development settings.
"""
import os
from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True

_replit_domains = [
    d.strip()
    for d in os.environ.get('REPLIT_DOMAINS', '').split(',')
    if d.strip()
]


INSTALLED_APPS += ['django_extensions'] if False else []  # noqa — enable by installing django-extensions

# Trust Replit's HTTPS proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Build CSRF trusted origins — cover both with and without explicit port
_replit_domains = [
    d.strip()
    for d in os.environ.get('REPLIT_DOMAINS', '').split(',')
    if d.strip()
]
CSRF_TRUSTED_ORIGINS = (
    # Exact domains from env — plain and with :8000
    [f'https://{d}' for d in _replit_domains]
    + [f'https://{d}:8000' for d in _replit_domains]
    + [
        # Wildcard subdomains (Django 4+ supports this)
        'https://*.replit.dev',
        'https://*.replit.dev:8000',
        'https://*.janeway.replit.dev',
        'https://*.janeway.replit.dev:8000',
        'https://*.repl.co',
        'http://localhost',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ]
)

ALLOWED_HOSTS = [
    'dd7b9d40-06d4-4c3b-abce-7b45423a365a-00-1khlf334e7v9p.janeway.replit.dev',
    'localhost',
    '127.0.0.1',
]

# Cookies must be marked secure since all traffic arrives via HTTPS proxy
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Supabase PostgreSQL — Session Pooler (IPv6-compatible)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.cdmnuffncwihkwisaggo',
        'PASSWORD': os.environ.get('SUPABASE_DB_PASSWORD', ''),
        'HOST': 'aws-1-eu-central-1.pooler.supabase.com',
        'PORT': '6543',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
