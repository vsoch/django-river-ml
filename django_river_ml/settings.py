from django.core.management.utils import get_random_secret_key
from django.conf import settings
import logging
import uuid
import os
import sys

logger = logging.getLogger(__name__)

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)

# Default views to Authenticate
authenticated_views = [
    "django_river_ml.views.learn.view",
    "django_river_ml.views.predict.view",
    "django_river_ml.views.model.view",
    "django_river_ml.views.metrics.view",
    "django_river_ml.views.metrics.stream_events",
    "django_river_ml.views.metrics.stream_metrics",
]


timed_views = ["django_river_ml.views.learn.view", "django_river_ml.views.predict.view"]

# Defaults for models and storage

backends = ["shelve", "redis"]


DEFAULTS = {
    # Url base prefix
    "URL_PREFIX": "api",
    # Model storage
    "STORAGE_BACKEND": "shelve",
    # Redis (if used)
    "REDIS_DB": "river-redis",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    # Base directory for storing secrets
    "APP_DIR": root,
    "CACHE_DIR": None,
    # Disable authentication
    "DISABLE_AUTHENTICATION": True,
    # Always generate identifiers for predictions
    # If set to False, you can still provide one to generate it
    "GENERATE_IDENTIFIERS": True,
    # Domain used in templates, api prefix
    "DOMAIN_URL": "http://127.0.0.1:8000",
    # The number of seconds a session (upload request) is valid (10 minutes)
    "SESSION_EXPIRES_SECONDS": 600,
    # The number of seconds a token is valid (10 minutes)
    "TOKEN_EXPIRES_SECONDS": 600,
    # Disable deletion of an image by tag or manifest (default is not disabled)
    # Default views to put under authentication, given that DISABLE_AUTHENTICTION is False
    "AUTHENTICATED_VIEWS": authenticated_views,
    # If you have a custom authentication server to generate tokens (defaults to /registry/auth/token
    "AUTHENTICATION_SERVER": None,
    # jwt encoding secret: set server wide or generated on the fly
    "JWT_SERVER_SECRET": str(uuid.uuid4()),
    # View rate limit, defaults to 100/1day using django-ratelimit based on ipaddress
    "VIEW_RATE_LIMIT": "10000/1d",
    # Given that someone goes over, are they blocked for a period?
    "VIEW_RATE_LIMIT_BLOCK": True,
    # Globally disable rate limit
    "VIEW_RATE_LIMIT_DISABLE": True,
    # Shelve and jwt keys (will be generated if not found)
    "SHELVE_SECRET_KEY": None,
    "JWT_SECRET_KEY": None,
    # Enable a custom set of views (by name)
    # If empty, all views are enabled
    "API_VIEWS_ENABLED": [],
}

# The user can define a section for django_river_ml in settings
CACHES = getattr(settings, "CACHES", [])
MIDDLEWARE = getattr(settings, "MIDDLEWARE", [])

ml = getattr(settings, "DJANGO_RIVER_ML", DEFAULTS)

# Add middleware to calculate times and stats
timer_middleware = "django_river_ml.middleware.timer_middleware"

if timer_middleware not in MIDDLEWARE:
    MIDDLEWARE.append(timer_middleware)

# Over-ride defaults with user settings!
for key, default in DEFAULTS.items():

    # If we find it in the environment, use this first
    value = os.environ.get(key)

    # Handle environment booleans
    if not value:
        value = ml.get(key, DEFAULTS[key])
    elif value.lower() == "true":
        value = True
    elif value == "false":
        value = False

    # Fall back to user settings and defaults
    locals()[key] = value

# Default shelve path is root of install - should be updated to be within app
SHELVE_PATH = ml.get("SHELVE_PATH", os.path.join(APP_DIR, "shelve.db"))

# Validation of django-river-ml settings
if STORAGE_BACKEND not in backends:
    sys.exit(
        "%s is not a valid storage backend, but me one of %s"
        % (STORAGE_BACKEND, " ".join(backends))
    )

# The database state will be held via settings
# db = None

# Generate secret key for shelve if used
def generate_secret_keys(filename):
    """
    A helper function to write a randomly generated secret key to file
    """
    with open(filename, "w") as fd:
        for keyname in ["SHELVE_SECRET_KEY", "JWT_SERVER_SECRET"]:
            key = get_random_secret_key()
            fd.writelines("%s = '%s'\n" % (keyname, key))


# **Important** this will generate in the install directory
# so recommended to already add to app settings.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Generate secret key for API (jwt) and shelve if do not exist, and not defined in environment
if not SHELVE_SECRET_KEY or not JWT_SERVER_SECRET:
    try:
        from .secret_key import SHELVE_SECRET_KEY, JWT_SERVER_SECRET
    except ImportError:
        generate_secret_keys(os.path.join(BASE_DIR, "secret_key.py"))
        from .secret_key import SHELVE_SECRET_KEY, JWT_SERVER_SECRET

# Create a filesystem cache for jwt tokens
cache = CACHE_DIR or os.path.join(APP_DIR, "cache")
if not os.path.exists(cache):
    logger.debug(f"Creating cache directory {cache}")
    os.makedirs(cache)

CACHES.update(
    {
        "django_river_ml": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": os.path.abspath(cache),
        }
    }
)

RATELIMIT_ENABLE = not VIEW_RATE_LIMIT_DISABLE
if not RATELIMIT_ENABLE:
    VIEW_RATE_LIMIT = None
