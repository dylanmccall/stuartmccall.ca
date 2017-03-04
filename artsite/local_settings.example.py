import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {}

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': '127.0.0.1:11211',
#     }
# }

# The site's absolute URL - used for emails and generated reports
SITE_URL = 'http://localhost:8000'

FROM_EMAIL = "stuartmccall.ca <noreply@example.com>"

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-ca'

TIME_ZONE = 'Canada/Pacific'

# ALLOWED_HOSTS = [
#     'localhost',
# ]

##### Development settings #####

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

##### Production settings #####

# SECRET_KEY = 'Your Very Secret Key'

# STATIC_ROOT = '/path/to/static/assets/directory/'
# STATIC_URL = SITE_URL+'/static/'

# MEDIA_ROOT = '/path/to/dynamic/media/directory/'
# MEDIA_URL = SITE_URL+'/media/'

# COMPRESS_PRECOMPILERS = (
#     ('text/less', '/path/to/node /path/to/lessc {infile} {outfile}'),
# )

# SERVER_EMAIL = "CBM Site Messages <admin@example.com>"
# ADMINS = [
#     ("Your Name", 'yourname@example.com'),
# ]

# DEBUG = False

# X_FRAME_OPTIONS = 'DENY'
# SECURE_CONTENT_TYPE_NOSNIFF = True

# CORS_ORIGIN_ALLOW_ALL = False

# Additional hardening for sites served over SSL:
# SECURE_SSL_REDIRECT = True
# SECURE_BROWSER_XSS_FILTER = True
# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True
# SESSION_COOKIE_SECURE = True
