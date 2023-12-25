import json

from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
from rest_framework.response import Response
from rest_framework.views import APIView

from django_river_ml import settings
from django_river_ml.auth import is_authenticated
from django_river_ml.client import RiverClient


class PredictView(APIView):
    """
    PredictView is a prediction API endpoint for a model.
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
        POST /api/predict/
        """
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return Response(status=400)

        # We generate an identifier for the user if not provided
        identifier = payload.get("identifier")
        model_name = payload.get("model")
        features = payload.get("features")

        allow_continue, response, _ = is_authenticated(request)
        if not allow_continue:
            return response

        if not model_name or not features:
            return Response(status=400, message="model and features are required.")

        client = RiverClient()
        success, data = client.predict(
            features=features, identifier=identifier, model_name=model_name
        )
        if not success:
            return Response(status=400, data=data)

        # An identifier was created for the prediction
        if "identifier" in data:
            return Response(status=201, data=data)
        return Response(status=200, data=data)
