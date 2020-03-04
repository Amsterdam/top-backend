from unittest.mock import patch, Mock
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from constance.test import override_config
from app.utils.unittest_helpers import get_authenticated_client, get_unauthenticated_client, get_test_user

class IsAuthenticatedViewTest(APITestCase):
    """
    Tests for the API endpoints for IsAuthenticatedView
    """

    @override_config(ALLOW_DATA_ACCESS=False)
    def test_safety_locked_request(self):
        """
        An request to check authentication should not be possible if
        the safety_lock (ALLOW_DATA_ACCESS) is on
        """
        url = reverse('is-authenticated')
        client = get_authenticated_client()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_requests(self):
        """
        is_authenticated is true when user is not logged in
        """
        url = reverse('is-authenticated')
        client = get_authenticated_client()
        response = client.get(url)

        expected_response = {
            'is_authenticated': True
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json(), expected_response)

    def test_unauthenticated_requests(self):
        """
        is_authenticated false when user is not logged in
        """
        url = reverse('is-authenticated')
        client = get_unauthenticated_client()
        response = client.get(url)

        expected_response = {
            'is_authenticated': False
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json(), expected_response)


class ObtainAuthTokenOIDCTest(APITestCase):
    """
    Tests for the API endpoints for optaining the OIDC access and refresh tokens
    """

    @override_config(ALLOW_DATA_ACCESS=False)
    def test_safety_locked_request(self):
        """
        A request should not be possible if the safety_lock (ALLOW_DATA_ACCESS) is on
        """
        url = reverse('oidc-authenticate')
        client = get_unauthenticated_client()
        response = client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_without_authentication_code(self):
        """
        fails if no authentication code is sent
        """
        url = reverse('oidc-authenticate')
        client = get_unauthenticated_client()
        response = client.post(url, {})

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('api.users.views.OIDCAuthenticationBackend')
    def test_with_authentication_code(self, mock_OIDCAuthenticationBackend):
        """
        succeeds if an authentication code is sent
        """
        mock_OIDCAuthenticationBackend.authenticate = Mock()
        mock_OIDCAuthenticationBackend.authenticate.return_value = get_test_user()

        url = reverse('oidc-authenticate')
        client = get_unauthenticated_client()
        response = client.post(url, {
            'code': 'FOO-CODE'
        })

        self.assertEquals(response.status_code, status.HTTP_200_OK)

    @patch('api.users.views.OIDCAuthenticationBackend')
    def test_with_authentication_code_response(self, mock_OIDCAuthenticationBackend):
        """
        Returns a refresh and access token if authentication is succesful
        """
        mock_OIDCAuthenticationBackend.authenticate = Mock()
        mock_OIDCAuthenticationBackend.authenticate.return_value = get_test_user()

        url = reverse('oidc-authenticate')
        client = get_unauthenticated_client()
        response = client.post(url, {
            'code': 'FOO-CODE'
        })

        token_response = response.json()

        # The response contains a refresh and an access token and a user object
        self.assertEquals(list(token_response.keys()), ['refresh', 'access', 'user'])
        self.assertIsNotNone(token_response['refresh'])
        self.assertIsNotNone(token_response['access'])
        self.assertIsNotNone(token_response['user'])

    @patch('api.users.views.OIDCAuthenticationBackend')
    def test_with_failing_authentication_code(self, mock_OIDCAuthenticationBackend):
        """
        Returns a bad request if the authentication using the code fails
        """
        # Mock the authenticate dependencies
        mock_authenticate = Mock()
        mock_OIDCAuthenticationBackend.return_value = mock_authenticate
        # Calling the authenticate calls a side effect containing an exception.
        # This should cause the authenticate request to fail
        mock_authenticate.authenticate = Mock(side_effect=Exception('FOO Exception'))

        url = reverse('oidc-authenticate')
        client = get_unauthenticated_client()
        response = client.post(url, {
            'code': 'FOO-CODE'
        })

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
