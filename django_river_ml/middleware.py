import time
from django.urls import resolve

from django_river_ml import settings as settings
import django_river_ml.storage as storage

from copy import deepcopy
import json

# The following are pre and post events that should be run alongside views
# to update either metrics or stats


def timer_middleware(get_response):
    """
    A custom class to start and end a counter.
    This should be used to decorate api.learn and api.predict
    """
    # One-time configuration and initialization.

    def middleware(request):

        # Derive the view name from the request PATH_INFO
        func, _, _ = resolve(request.META["PATH_INFO"])
        view_name = "%s.%s" % (func.__module__, func.__name__)
        in_timed_view = view_name in settings.timed_views

        # Grab the started at time
        started_at = time.perf_counter_ns()

        # Deep copy the request body to see if we hav a name param
        model_name = None
        try:
            copied = deepcopy(request.body)
            payload = json.loads(copied.decode("utf-8"))
            model_name = payload.get("model")
        except:
            pass

        response = get_response(request)

        # Cut out early if not in a timed view
        if not in_timed_view or not model_name:
            return response

        # Calculate the duration and add to stats
        duration = time.perf_counter_ns() - started_at
        db = storage.get_db()
        if f"stats/{model_name}" not in db:
            storage.init_stats(model_name)
        stats = db[f"stats/{model_name}"]

        if request.path == "/%s/learn/" % settings.URL_PREFIX:
            stats["learn_mean"].update(duration)
            stats["learn_ewm"].update(duration)
        elif request.path == "/%s/predict/" % settings.URL_PREFIX:
            stats["predict_mean"].update(duration)
            stats["predict_ewm"].update(duration)

        db[f"stats/{model_name}"] = stats
        return response

    return middleware
