from django.apps import AppConfig


class DjangoRiverMLConfig(AppConfig):
    name = "django_river_ml"
    verbose_name = "River Online Machine Learning for Django"

    def ready(self):
        import django_river_ml.signals

        assert django_river_ml.signals
