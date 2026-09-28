import requests_mock
from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from utils.unittest_helpers import get_test_user, get_unauthenticated_client

ZAKEN_API_URL = "https://aza.nl/api/v1"
BAG_ID = "0363010000828554"
PUNTENTELLING_ID = "42"


def get_force_authenticated_client():
    client = APIClient()
    client.force_authenticate(user=get_test_user())
    return client


@override_settings(ZAKEN_API_URL=ZAKEN_API_URL)
class PuntentellerViewSetTest(APITestCase):
    def test_unauthenticated_get_address_is_rejected(self):
        url = reverse("v1:puntenteller-address", kwargs={"bag_id": BAG_ID})
        client = get_unauthenticated_client()

        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @requests_mock.Mocker()
    def test_get_address_forwards_query_params(self, mocker):
        mocker.get(
            f"{settings.ZAKEN_API_URL}/puntenteller/adressen/{BAG_ID}/",
            json={"results": [{"bag_id": BAG_ID}]},
            status_code=200,
        )

        client = get_force_authenticated_client()
        response = client.get(
            reverse("v1:puntenteller-address", kwargs={"bag_id": BAG_ID}),
            {"limit": 10, "offset": 20},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"results": [{"bag_id": BAG_ID}]})
        self.assertEqual(mocker.last_request.qs, {"limit": ["10"], "offset": ["20"]})

    @requests_mock.Mocker()
    def test_post_address_forwards_request_body(self, mocker):
        payload = {"woonoppervlakte": 52, "heeft_lift": True}
        mocker.post(
            f"{settings.ZAKEN_API_URL}/puntenteller/adressen/{BAG_ID}/",
            json={"id": 1, **payload},
            status_code=201,
        )

        client = get_force_authenticated_client()
        response = client.post(
            reverse("v1:puntenteller-address", kwargs={"bag_id": BAG_ID}),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {"id": 1, **payload})
        self.assertEqual(mocker.last_request.json(), payload)

    @requests_mock.Mocker()
    def test_get_invoerwaarden_proxies_response(self, mocker):
        expected_response = {"categorieen": [{"naam": "Woonruimte"}]}
        mocker.get(
            f"{settings.ZAKEN_API_URL}/puntenteller/adressen/{BAG_ID}/invoerwaarden/",
            json=expected_response,
            status_code=200,
        )

        client = get_force_authenticated_client()
        response = client.get(
            reverse("v1:puntenteller-invoerwaarden", kwargs={"bag_id": BAG_ID})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response)

    @requests_mock.Mocker()
    def test_patch_puntentelling_forwards_request_body(self, mocker):
        payload = {"punten": 143}
        mocker.patch(
            f"{settings.ZAKEN_API_URL}/puntenteller/puntentellingen/{PUNTENTELLING_ID}/",
            json={"id": int(PUNTENTELLING_ID), **payload},
            status_code=200,
        )

        client = get_force_authenticated_client()
        response = client.patch(
            reverse(
                "v1:puntenteller-puntentelling",
                kwargs={"id": PUNTENTELLING_ID},
            ),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"id": int(PUNTENTELLING_ID), **payload})
        self.assertEqual(mocker.last_request.json(), payload)
