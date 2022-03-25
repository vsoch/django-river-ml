from django.urls import path
import tests.example.views as views

urlpatterns = [
    path("", views.index),
    path("data/model/clusters/<str:name>/", views.get_centroids, name="model_clusters"),
]
