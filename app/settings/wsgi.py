import os

from django.core.wsgi import get_wsgi_application

from .logging import start_logging

start_logging()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

application = get_wsgi_application()
