from rest_framework.views import APIView
from rest_framework.response import Response

from django_river_ml import settings

from ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from django_river_ml.client import RiverClient
import json


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
        except:
            return Response(status=400)

        model_name = payload.get("model")
        identifier = payload.get("identifier")
        features = payload.get("features")

        if not model_name or not features:
            return Response(status=400, message="model and features are required.")

        client = RiverClient()
        success, data = client.predict(
            features=features, identifier=identifier, model_name=model_name
        )
        if not success:
            return Response(status=400, data=data)
        if data["created"]:
            return Response(status=201, data=data)
        return Response(status=200, data=data)
