from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import StreamingHttpResponse

from ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django_river_ml.client import RiverClient
import django_river_ml.settings as settings

import json


class MetricsView(APIView):
    """
    Get metrics for a database
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
        """
        GET /api/metrics/
        """
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except:
            return Response(status=400)

        model_name = payload.get("model")
        if not model_name:
            return Response(status=400)

        client = RiverClient()
        return Response(status=200, data=client.metrics(model_name))


@require_http_methods(["GET"])
@ratelimit(
    key="ip", block=settings.VIEW_RATE_LIMIT_BLOCK, rate=settings.VIEW_RATE_LIMIT
)
def stream_metrics(request):
    """GET /api/stream/metrics/"""
    client = RiverClient()
    return StreamingHttpResponse(
        client.stream_metrics(), content_type="text/event-stream"
    )


@require_http_methods(["GET"])
@ratelimit(
    key="ip", block=settings.VIEW_RATE_LIMIT_BLOCK, rate=settings.VIEW_RATE_LIMIT
)
def stream_events(request):
    """
    GET /api/stream/events/
    """
    client = RiverClient()
    return StreamingHttpResponse(
        client.stream_events(), content_type="text/event-stream"
    )


class StatsView(APIView):
    """
    Get stats for the database
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
        """
        GET /api/stats/
        """
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except:
            return Response(status=400)

        model_name = payload.get("model")
        if not model_name:
            return Response(status=400)

        client = RiverClient()
        found, stats = client.stats(model_name)
        if not found:
            return Response(status=404, data={"message": stats})
        return Response(status=200, data=stats)
