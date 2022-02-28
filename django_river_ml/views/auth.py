from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from django.http import HttpResponseForbidden

import django_river_ml.auth as auth


@authentication_classes([])
@permission_classes([])
class GetAuthToken(APIView):
    """
    Given a GET request for a token, validate and return it.
    """

    permission_classes = []
    allowed_methods = ("GET",)

    def get(self, request, *args, **kwargs):
        """GET /auth/token"""
        print("GET /auth/token")
        user = auth.get_user(request)

        # No token provided matching a user, no go
        if not user:
            return HttpResponseForbidden()

        # Generate the token data, a dict with token, expires_in, and issued_at
        data = auth.generate_jwt(user.username)
        return Response(status=200, data=data)
