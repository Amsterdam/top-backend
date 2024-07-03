from apps.health.utils import assert_health_generic, get_health_response
from django.conf import settings
from django.http import HttpResponse

SUCCESS_DICTIONARY_DEFAULT = {"message": "Connectivity OK"}


def health_default(request):
    def assert_default_health():
        assert_health_generic(database_name=settings.DEFAULT_DATABASE_NAME)

    return get_health_response(assert_default_health, SUCCESS_DICTIONARY_DEFAULT)


def is_healthy(request):
    return HttpResponse("Ok", content_type="text/plain", status=200)
