from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"", include("django_river_ml.urls", namespace="django_river_ml")),
]
