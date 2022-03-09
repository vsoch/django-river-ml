from rest_framework.views import APIView
from rest_framework.response import Response

from django.http import QueryDict, HttpResponse

from django_river_ml import settings as settings
from django_river_ml.client import RiverClient
from django_river_ml import model as models
from django_river_ml.auth import is_authenticated

from ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import dill


class ModelDownloadView(APIView):
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
        GET /api/model/download/<name>/
        """
        allow_continue, response, _ = is_authenticated(request)
        if not allow_continue:
            return response

        name = kwargs.get("name")
        if not name:
            return Response(status=400, data={"message": "A model name is required"})
        client = RiverClient()
        model = client.get_model(name)
        if not model:
            return Response(status=404)
        return HttpResponse(dill.dumps(model), content_type="application/octet-stream")


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
        GET /api/model/<name>/
        """
        allow_continue, response, _ = is_authenticated(request)
        if not allow_continue:
            return response

        name = kwargs.get("name")
        if not name:
            return Response(status=400, data={"message": "A model name is required"})
        client = RiverClient()
        model = client.get_model(name)

        # We can't find that model!
        if not model:
            return Response(status=404)

        dumped = models.model_to_dict(model)
        return Response(status=200, data=dumped)

    def post(self, request, *args, **kwargs):
        """
        POST /api/model/<flavor>/<name>
        """
        allow_continue, response, _ = is_authenticated(request)
        if not allow_continue:
            return response

        name = None

        # if we only have one arg, we have flavor
        if len(kwargs) == 1:
            flavor = kwargs.get("name")

        # if we only have one arg, we have flavor
        elif len(kwargs) == 2:
            flavor = kwargs.get("flavor")
            name = kwargs.get("name")

        model = dill.loads(request.body)
        client = RiverClient()
        added, data = client.add_model(model, name=name, flavor=flavor)
        if added:
            return Response(status=201, data=data)
        return Response(status=400, data=data)

    def delete(self, request, *args, **kwargs):
        """
        DELETE /api/model/
        """
        params = QueryDict(request.body)
        name = params.get("model")

        allow_continue, response, _ = is_authenticated(request)
        if not allow_continue:
            return response

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
        allow_continue, response, _ = is_authenticated(request)
        if not allow_continue:
            return response

        client = RiverClient()
        return Response(status=200, data=client.models())
