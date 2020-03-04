from django.http import HttpResponseBadRequest
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from api.users.auth import OIDCAuthenticationBackend
from utils.safety_lock import safety_lock


class IsAuthenticatedView(APIView):
    permission_classes = ()

    @safety_lock
    def get(self, request):
        permission_class = IsAuthenticated()
        is_authenticated = permission_class.has_permission(request, self)
        return Response({'is_authenticated': is_authenticated})


class ObtainAuthTokenOIDC(APIView):
    permission_classes = ()

    @safety_lock
    def post(self, request, *args, **kwargs):
        code = request.data.get('code', None)

        if not code:
            return HttpResponseBadRequest('No authentication code found')

        authentication_backend = OIDCAuthenticationBackend()

        try:
            user = authentication_backend.authenticate(request)
        except Exception as e:
            print(e)
            return HttpResponseBadRequest('Could not authenticate')

        refresh = RefreshToken.for_user(user)
        return Response(
            {'refresh': str(refresh),
             'access': str(refresh.access_token)}
        )


obtain_auth_token = ObtainAuthTokenOIDC.as_view()
