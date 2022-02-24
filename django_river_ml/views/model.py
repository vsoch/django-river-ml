from rest_framework.views import APIView
from rest_framework.response import Response

from django.http import QueryDict

from django_river_ml import settings as settings
from django_river_ml.client import RiverClient

from ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import dill


class ModelView(APIView):
    permission_classes = []
    allowed_methods = ("GET", "POST", "DELETE")

    @method_decorator(
        ratelimit(
            key="ip",
            rate=settings.VIEW_RATE_LIMIT,
            method="GET",
            block=settings.VIEW_RATE_LIMIT_BLOCK,
        )
    )
    def get(self, request, *args, **kwargs):
        """
        GET /api/model/<name>
        """
        name = kwargs.get("name", settings.MODEL_DEFAULT_NAME)
        client = RiverClient()
        model = client.get_model(name)
        return Response(status=200, data=dill.dumps(model))

    def post(self, request, *args, **kwargs):
        """
        POST /api/model/<name>
        """
        model = dill.loads(request.body)
        client = RiverClient()
        data = client.add_model(model)
        return Response(status=201, data=data)

    def delete(self, request, *args, **kwargs):
        """
        DELETE /api/model/<name>
        """
        params = QueryDict(request.body)
        name = params.get("name")
        client = RiverClient()
        if not client.delete_model(name):
            return Response(status=404)
        return Response(204)


class ModelsView(APIView):
    permission_classes = []
    allowed_methods = ("GET",)

    @method_decorator(
        ratelimit(
            key="ip",
            rate=settings.VIEW_RATE_LIMIT,
            method="GET",
            block=settings.VIEW_RATE_LIMIT_BLOCK,
        )
    )
    def get(self, request, *args, **kwargs):
        """
        GET /api/models/
        """
        client = RiverClient()
        return Response(status=200, data=client.models())
