import logging

import requests
from apps.users.utils import get_auth_header_from_request
from django.conf import settings
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from utils.queries_zaken_api import get_headers

from .serializers import FeedbackSerializer

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30

APP_NAME = "TOP"


class FeedbackView(GenericAPIView):
    """
    Forwards feedback submissions to the Zaken backend.
    """

    serializer_class = FeedbackSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = {**serializer.validated_data, "app_name": APP_NAME}

        response = requests.post(
            f"{settings.ZAKEN_API_URL}/feedback/",
            json=data,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            headers=get_headers(get_auth_header_from_request(request)),
        )
        response.raise_for_status()

        return Response(status=response.status_code)
