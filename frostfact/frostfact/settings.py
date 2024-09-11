
from pathlib import Path
from dotenv import load_dotenv
import os
import sys
from datetime import timedelta
import base64
from django.contrib.auth.apps import AuthConfig
import dj_database_url
import logging
import redis

logger = logging.getLogger('__main__')

ENVIRONMENT = str(os.getenv('ENVIRONMENT', 'development'))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv('DEV_DATABASE_URL')
if ENVIRONMENT in ['development', 'staging']:
    from dotenv import load_dotenv
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

# SECURITY WARNING: keep the secret key used in production secret!



CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]


SECRET_KEY = str(os.getenv('DJANGO_SECRET_KEY'))


AWS_ACCESS_KEY_ID = str(os.getenv('AWS_ACCESS_KEY_ID'))
AWS_SECRET_ACCESS_KEY = str(os.getenv('AWS_SECRET_ACCESS_KEY'))
AWS_STORAGE_BUCKET_NAME = str(os.getenv('AWS_STORAGE_BUCKET_NAME'))
AWS_S3_SIGNATURE_VERSION = str(os.getenv("AWS_S3_SIGNATURE_VERSION", "s3v4"))
AWS_S3_OBJECT_PARAMETERS = {
    'ACL': 'public-read',
}
AWS_S3_REGION_NAME = str(os.getenv("AWS_S3_REGION_NAME"))
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

MEDIAFILES_LOCATION = 'media/'

if ENVIRONMENT == 'production':
    print(ENVIRONMENT)
    DATABASE_URL = os.getenv('DATABASE_URL')
    DEBUG = False
    ALLOWED_HOSTS = ['.herokuapp.com','.frostfactorybk.com']
    DATABASES = {
        'default': dj_database_url.config(
            default=str(DATABASE_URL),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',  # Add this if your server requires SSL/TLS
    }
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_SSL_REDIRECT = True

    redis_url = os.getenv('CACHETOGO_URL')

    redis_client = redis.Redis.from_url(redis_url)

    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': redis_url,  # Use the Cache To Go URL
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'IGNORE_EXCEPTIONS': True,
            }
        }
    }
    CACHE_MIDDLEWARE_SECONDS = 300

    print(redis_url)

    CORS_ALLOWED_ORIGINS = [
        'https://frostfactorybk.com',
        'https://api.frostfactorybk.com',
    ]
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^https://\w+\.frostfactorybk\.com$",
    ]

elif ENVIRONMENT == 'staging':
    print(ENVIRONMENT)
    DATABASE_URL = os.getenv('DEV_DATABASE_URL')
    DEBUG = True  # Set to False if you want staging to behave like production
    ALLOWED_HOSTS = ['.herokuapp.com', '.frostfactorybk.com']
    DATABASES = {
        'default': dj_database_url.config(
            default=str(DATABASE_URL),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',  # Add this if your server requires SSL/TLS
    }
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_SSL_REDIRECT = True
    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^https://.*$",
        r"^http://.*$",
    ]

    redis_url = os.getenv('CACHETOGO_URL')

    redis_client = redis.Redis.from_url(redis_url)

    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': redis_url,  # Use the Cache To Go URL
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'IGNORE_EXCEPTIONS': True,
            }
        }
    }
    CACHE_MIDDLEWARE_SECONDS = 300


else:


    DATABASE_URL = os.getenv('DATABASE_URL')
    print(f'this is the database in dev {DATABASE_URL}')
    CORS_ORIGIN_ALLOW_ALL = True
    DEBUG = True
    ALLOWED_HOSTS = ['*']


    DATABASES = {
        'default': dj_database_url.config(
            default=str(DATABASE_URL),
            conn_max_age=600,
            conn_health_checks=True,

        )
    }

    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',  # Ensure sslmode is set to 'require'
    }




CACHE_TTL = 60 * 60 * 24  # Cache timeout set to 24 hours
INSTALLED_APPS = [
    "admin_interface",
    "colorfield",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "corsheaders",
    'rest_framework',
    'frostapi',
    'storages',



]

print(ENVIRONMENT, 'dev testing')



AuthConfig.verbose_name = "User Authorization"
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',

]

ROOT_URLCONF = 'frostfact.urls'

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

WSGI_APPLICATION = 'frostfact.wsgi.application'




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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'frostapi.authentication.CustomHeaderAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # drf-spectacular settings
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

API_TOKEN_USER_AUTH_KEY = os.environ.get('API_TOKEN_USER_AUTH_KEY')
API_TOKEN_USER_AUTH_VALUE = os.environ.get('API_TOKEN_USER_AUTH_VALUE')

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DATE_FORMAT = '%m-%d-%Y'

TIME_FORMAT = "%H:%M"

USE_L10N = False


STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

logger.info(f"Connecting to the database with URL: {DATABASE_URL}")
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIAFILES_LOCATION}/'

# MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CSRF_COOKIE_NAME = 'XSRF-TOKEN'
CSRF_HEADER_NAME = 'HTTP_X_XSRF_TOKEN'

X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]






LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'frostapi': {  # Replace 'your_app_name' with your actual app name
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}




