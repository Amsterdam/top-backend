import logging

import requests
from django.conf import settings
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable
from settings.celery import debug_task
from utils import queries_brk_api as brk_api

logger = logging.getLogger(__name__)


class APIServiceCheckBackend(BaseHealthCheckBackend):
    """
    Generic base class for checking API services
    """

    critical_service = False
    api_url = None
    api_url_suffix = ""
    verbose_name = None

    def check_status(self):
        """Check service by opening and closing a broker channel."""
        logger.debug("Checking status of API url...")
        try:
            assert self.api_url, "The given api_url should be set"
            response = requests.get(f"{self.api_url}{self.api_url_suffix}")
            response.raise_for_status()
        except AssertionError as e:
            self.add_error(
                ServiceUnavailable("The given API endpoint has not been set"),
                e,
            )
        except ConnectionRefusedError as e:
            self.add_error(
                ServiceUnavailable("Unable to connect to API: Connection was refused."),
                e,
            )
        except BaseException as e:
            self.add_error(ServiceUnavailable("Unknown error"), e)
        else:
            logger.debug("Connection established. API is healthy.")

    def identifier(self):
        if self.verbose_name:
            return self.verbose_name

        return self.__class__.__name__


class BAGServiceCheck(APIServiceCheckBackend):
    """
    Endpoint for checking the BAG Service API Endpoint
    """

    critical_service = True
    api_url = settings.BAG_API_SEARCH_URL
    verbose_name = "BAG API"


class ZakenServiceCheck(APIServiceCheckBackend):
    """
    Endpoint for checking the Zken API Endpoint
    """

    critical_service = True
    api_url = settings.ZAKEN_API_HEALTH_URL
    verbose_name = "Zaken API Endpoint"


class VakantieverhuurHitkansServiceCheck(APIServiceCheckBackend):
    """
    Endpoint for checking vakantieverhuur fraudpredictions API Endpoint
    """

    critical_service = False
    api_url = settings.VAKANTIEVERHUUR_HITKANS_HEALTH_URL
    verbose_name = "Vakantieverhuur fraudpredictions API Endpoint"


class OnderhuurHitkansServiceCheck(APIServiceCheckBackend):
    """
    Endpoint for checking onderhuurverhuur fraudpredictions API Endpoint
    """

    critical_service = False
    api_url = settings.ONDERHUUR_HITKANS_HEALTH_URL
    verbose_name = "Onderhuur fraudpredictions API Endpoint"


class CeleryExecuteTask(BaseHealthCheckBackend):
    def check_status(self):
        result = debug_task.apply_async(ignore_result=False)
        assert result, "Debug task executes successfully"


class BRKServiceCheck(BaseHealthCheckBackend):
    """
    Endpoint for checking the BRK Service API Endpoint
    """

    critical_service = False

    def check_status(self):
        try:
            api_response = brk_api.request_brk_data(settings.BAG_ID_AMSTEL_1)
            assert api_response, "BRK API connection Failed"
        except Exception as e:
            self.add_error(ServiceUnavailable("BRK API connection failed"), e)
            logger.error("BRK API connection failed: %s", e)
        else:
            logger.info("BRK API connection is healthy.")

    def identifier(self):
        return "BRK API"
