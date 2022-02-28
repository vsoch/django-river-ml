from django_river_ml import settings
import abc
import contextlib
import os
import shelve

import river.base
import river.metrics
import river.stats
import river.utils
import dill
import redis

import logging

logger = logging.getLogger(__name__)

from . import exceptions
from . import flavors
from . import namer


class StorageBackend(abc.ABC):
    """Abstract storage backend.

    This interface defines a set of methods to implement in order for a database to be used as a
    storage backend. This allows using different databases in a homogeneous manner by proving a
    single interface. Since online-ml models are largely defined by Python dictionaries, we use
    key value store databases like redis.

    """

    @abc.abstractmethod
    def __setitem__(self, key, obj):
        """Store an object."""

    @abc.abstractmethod
    def __getitem__(self, key):
        """Retrieve an object."""

    @abc.abstractmethod
    def __delitem__(self, key):
        """Remove an object from storage."""

    @abc.abstractmethod
    def __iter__(self):
        """Iterate over the keys."""

    @abc.abstractmethod
    def close(self):
        """Do something when the app shuts down."""

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


class ShelveBackend(shelve.DbfilenameShelf, StorageBackend):  # type: ignore
    """Storage backend based on the shelve module from the standard library.

    This should mainly be used for development and testing, but not production.

    """


class RedisBackend(StorageBackend):
    """Redis is the suggest backend for a more production database."""

    def __init__(self, host, port, db):
        self.r = redis.Redis(host=host, port=port, db=db)

    def __setitem__(self, key, obj):
        self.r[key] = dill.dumps(obj)

    def __getitem__(self, key):
        return dill.loads(self.r[key])

    def __delitem__(self, key):
        self.r.delete(key)

    def __iter__(self):
        for key in self.r.scan_iter():
            yield key.decode()

    def close(self):
        return


# The following will make it so that shelve.open returns ShelveBackend instead of DbfilenameShelf
shelve.DbfilenameShelf = ShelveBackend  # type: ignore


def get_db() -> StorageBackend:
    """
    Get the database, an attribute of settings.
    """
    if not hasattr(settings, "db"):
        backend = settings.STORAGE_BACKEND

        if backend == "shelve":
            settings.db = shelve.open(settings.SHELVE_PATH)

        elif backend == "redis":
            settings.db = RedisBackend(
                host=settings.REDIS_HOST,
                port=int(settings.REDIS_PORT),
                db=int(settings.REDIS_DB),
            )
        else:
            raise ValueError(f"Unknown storage backend: {backend}")

    return settings.db


def close_db(e=None):
    if hasattr(settings, "db"):
        if settings.db is not None:
            settings.db.close()
        delattr(settings, "db")


def drop_db():
    """This function's responsability is to wipe out a database.

    This could be implement within each StorageBackend, it's just a bit more akward because at this
    point the database connection is not stored in the app anymore.
    """
    backend = settings.STORAGE_BACKEND

    if backend == "shelve":
        path = settings.SHELVE_PATH
        with contextlib.suppress(FileNotFoundError):
            os.remove(f"{path}")

    elif backend == "redis":
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=int(settings.REDIS_PORT or 6379),
            db=int(settings.REDIS_DB or 0),
        )
        r.flushdb()


def set_flavor(flavor: str, name: str):
    try:
        flavor = flavors.allowed_flavors()[flavor]
    except KeyError:
        raise exceptions.UnknownFlavor

    db = get_db()
    db[f"flavor/{name}"] = flavor


def init_stats(name: str):
    db = get_db()
    db[f"stats/{name}"] = {
        "learn_mean": river.stats.Mean(),
        "learn_ewm": river.stats.EWMean(0.3),
        "predict_mean": river.stats.Mean(),
        "predict_ewm": river.stats.EWMean(0.3),
    }


def init_metrics(name: str):
    db = get_db()
    try:
        flavor = db[f"flavor/{name}"]
    except KeyError:
        raise exceptions.FlavorNotSet
    db[f"metrics/{name}"] = flavor.default_metrics()


def add_model(model: river.base.Estimator, flavor: str, name: str = None) -> str:
    db = get_db()

    # Pick a name if none is given
    if name is None:
        while True:
            name = _random_slug()
            if f"models/{name}" not in db:
                break

    # Make sure flavor is valid before continuing
    # it will be associated with the model name
    set_flavor(flavor=flavor, name=name)
    db[f"models/{name}"] = model

    init_stats(name)
    init_metrics(name)
    return name


def delete_model(name: str):
    db = get_db()
    del db[f"models/{name}"]
    del db[f"stats/{name}"]
    del db[f"metrics/{name}"]


def _random_slug() -> str:
    return namer.namer.generate()
