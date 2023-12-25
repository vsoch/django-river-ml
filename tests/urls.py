# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from django.urls import include, path

from tests.example.urls import urlpatterns as example_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("django_river_ml.urls", namespace="django_river_ml")),
]

urlpatterns += example_urls
