import river
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
from rest_framework.response import Response
from rest_framework.views import APIView

from django_river_ml import settings
from django_river_ml.version import __version__


class ServiceInfo(APIView):
    """
    provide version support information based on response statuses.
    """

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
        print("GET /api/")

        data = {
            "id": "django_river_ml",
            "status": "running",
            "name": "Django River ML Endpoint",
            "description": "This service provides an api for models",
            "documentationUrl": "https://vsoch.github.io/django-river-ml",
            "storage": settings.STORAGE_BACKEND,
            "river_version": river.__version__,
            "version": __version__,
        }
        return Response(status=200, data=data)
