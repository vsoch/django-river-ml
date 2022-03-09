from django.urls import path
from django_river_ml import views
from django_river_ml import settings

app_name = "django_river_ml"

urlpatterns = []
contenders = [
    path(
        "%s/auth/token/" % settings.URL_PREFIX,
        views.GetAuthToken.as_view(),
        name="auth_token",
    ),
    path(
        "%s/" % settings.URL_PREFIX,
        views.ServiceInfo.as_view(),
        name="service_info",
    ),
    path(
        "%s/learn/" % settings.URL_PREFIX,
        views.LearnView.as_view(),
        name="learn",
    ),
    path(
        "%s/predict/" % settings.URL_PREFIX,
        views.PredictView.as_view(),
        name="predict",
    ),
    path(
        "%s/label/" % settings.URL_PREFIX,
        views.LabelView.as_view(),
        name="label",
    ),
    path(
        "%s/metrics/" % settings.URL_PREFIX,
        views.MetricsView.as_view(),
        name="metrics",
    ),
    path(
        "%s/stream/metrics/" % settings.URL_PREFIX,
        views.stream_metrics,
        name="stream_metrics",
    ),
    path(
        "%s/stream/events/" % settings.URL_PREFIX,
        views.stream_events,
        name="stream_events",
    ),
    path(
        "%s/stats/" % settings.URL_PREFIX,
        views.StatsView.as_view(),
        name="stats",
    ),
    path(
        "%s/model/download/<str:name>/" % settings.URL_PREFIX,
        views.ModelDownloadView.as_view(),
        name="model_download",
    ),
    path(
        "%s/model/" % settings.URL_PREFIX,
        views.ModelView.as_view(),
        name="model",
    ),
    path(
        "%s/model/<str:name>/" % settings.URL_PREFIX,
        views.ModelView.as_view(),
        name="model",
    ),
    path(
        "%s/model/<str:flavor>/<str:name>/" % settings.URL_PREFIX,
        views.ModelView.as_view(),
        name="model",
    ),
    path(
        "%s/models/" % settings.URL_PREFIX,
        views.ModelsView.as_view(),
        name="models",
    ),
]

# If this variable isn't set, we set all of them
if not settings.API_VIEWS_ENABLED:
    urlpatterns = contenders

# Otherwise, the user can choose to expose only a subset of urls
else:
    for url in contenders:
        if (
            url.name in settings.API_VIEWS_ENABLED
            or url.pattern.name in settings.API_VIEWS_ENABLED
        ):
            urlpatterns.append(url)
