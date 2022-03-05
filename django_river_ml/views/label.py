from rest_framework.views import APIView
from rest_framework.response import Response

from django_river_ml import settings
from django_river_ml.auth import is_authenticated

from ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from django_river_ml.client import RiverClient
import json


class LabelView(APIView):
    """
    Apply a label to a previous prediction.
    """

    permission_classes = []
    allowed_methods = ("POST",)

    @method_decorator(
        ratelimit(
            key="ip",
            rate=settings.VIEW_RATE_LIMIT,
            method="POST",
            block=settings.VIEW_RATE_LIMIT_BLOCK,
        )
    )
    def post(self, request, *args, **kwargs):
        """
        POST /api/label/
        """
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except:
            return Response(status=400)

        model_name = payload.get("model")
        identifier = payload.get("identifier")
        label = payload.get("label")

        allow_continue, response, _ = is_authenticated(request)
        if not allow_continue:
            return response

        if not model_name or not label or not identifier:
            return Response(
                status=400, message="model, label, and identifier are required."
            )

        client = RiverClient()
        success, data = client.label(
            label=label, identifier=identifier, model_name=model_name
        )
        if not success:
            return Response(status=400, data=data)
        return Response(status=200, data=data)
