from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.cache import never_cache
from django.http import StreamingHttpResponse

from ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django_river_ml.client import RiverClient
import django_river_ml.settings as settings


class MetricsView(APIView):
    """
    Get metrics for a database
    """

    permission_classes = []
    allowed_methods = ("GET",)

    @never_cache
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
        client = RiverClient()
        return Response(status=200, data=client.metrics())


@never_cache
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


@never_cache
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

    @never_cache
    @method_decorator(
        ratelimit(
            key="ip",
            rate=settings.VIEW_RATE_LIMIT,
            method="GET",
            block=settings.VIEW_RATE_LIMIT_BLOCK,
        )
    )
    def get(self, request, *args, **kwargs):
        """GET /api/stats/"""

        client = RiverClient()
        return Response(status=200, data=client.stats())
