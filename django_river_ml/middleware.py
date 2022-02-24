import time

from django_river_ml import settings as settings
import django_river_ml.storage as storage

# The following are pre and post events that should be run alongside views
# to update either metrics or stats


def timer_middleware(get_response):
    """
    A custom class to start and end a counter.
    This should be used to decorate api.learn and api.predict
    """
    # One-time configuration and initialization.

    def middleware(request):

        # Grab the started at time
        started_at = time.perf_counter_ns()
        response = get_response(request)

        # Calculate the duration and add to stats
        duration = time.perf_counter_ns() - started_at
        db = storage.get_db()
        stats = db["stats"]

        print(request.path)
        if request.path == "/%s/learn/" % settings.URL_PREFIX:
            stats["learn_mean"].update(duration)
            stats["learn_ewm"].update(duration)
        elif request.path == "/%s/predict/" % settings.URL_PREFIX:
            stats["predict_mean"].update(duration)
            stats["predict_ewm"].update(duration)

        db["stats"] = stats
        return response

    return middleware
