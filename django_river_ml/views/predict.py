from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.cache import never_cache

from django_river_ml import settings
from django.http import QueryDict

from ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from django_river_ml.client import RiverClient


class PredictView(APIView):
    """
    PredictView is a prediction API endpoint for a model.
    """

    permission_classes = []
    allowed_methods = ("POST",)

    @never_cache
    @method_decorator(
        ratelimit(
            key="ip",
            rate=settings.VIEW_RATE_LIMIT,
            method="POST",
            block=settings.VIEW_RATE_LIMIT_BLOCK,
        )
    )
    @never_cache
    def post(self, request, *args, **kwargs):
        """
        POST /api/predict/
        """
        payload = QueryDict(request.body)

        model_name = payload.get("model")
        identifier = payload.get("identifier")
        features = payload.get("features")

        client = RiverClient()
        data = client.predict(
            features=features, identifier=identifier, model_name=model_name
        )
        if not data:
            return Response(status=400)
        if data["created"]:
            return Response(status=201, data=data)
        return Response(status=200, data=data)
