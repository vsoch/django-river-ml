from rest_framework.views import APIView
from rest_framework.response import Response

from django_river_ml import settings
from django_river_ml.auth import is_authenticated
from ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from django_river_ml.client import RiverClient

import json


class LearnView(APIView):
    """
    LearnView is a learning API endpoint for a model.
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
        POST /api/learn/
        """
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except:
            return Response(status=400)

        allow_continue, response, _ = is_authenticated(request)
        if not allow_continue:
            return response

        model_name = payload.get("model")
        features = payload.get("features")
        prediction = payload.get("prediction")
        ground_truth = payload.get("ground_truth")
        identifier = payload.get("identifier")

        if not model_name or not features:
            return Response(
                status=400, data={"message": "model and features are required."}
            )

        # Create a client to interact with the database / announcers
        client = RiverClient()

        # This will either return a result object or raise an exception
        success, data = client.learn(
            prediction=prediction,
            features=features,
            model_name=model_name,
            identifier=identifier,
            ground_truth=ground_truth,
        )
        if not success:
            return Response(status=400, data=data)
        return Response(status=201, data=data)
