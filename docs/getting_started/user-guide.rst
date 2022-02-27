.. _getting_started-user-guide:

==========
User Guide
==========

Django River ML allows you to easily deploy `river <https://riverml.xyz>`_ online machine learning
for a `Django <https://www.djangoproject.com/>`_ project. It is based off of `chantilly <https://github.com/online-ml/chantilly>`_ 
with hopes of having similar design. We include `example clients <https://github.com/vsoch/django-river-ml/tree/main/examples>`_ and a 
test application in `tests <https://github.com/vsoch/django-river-ml/tree/main/tests>`_.
We are excited about what you might build with this, and please
`give us a ping <https://github.com/US-RSE/usrse-python>`_. if you have a question, find a bug, or want to request a feature!
This is an open source project and we are eager for your contribution. 🎉️

Quick Start
===========

Once you have ``django-river-ml`` installed (:ref:`getting_started-installation`) you
can do basic setup.

Setup
-----

Add it to your ``INSTALLED_APPS`` along with ``rest_framework``


.. code-block:: python


    INSTALLED_APPS = (
        ...
        'django_river_ml',
        'rest_framework',
        ...
    )


Add django-river-ml's URL patterns:

.. code-block:: python

    from django_river_ml import urls as django_river_urls
    urlpatterns = [
        ...
        url(r'^', include(django_river_urls)),
        ...
    ]


Settings
--------

It is highly recommended that you minimally set these settings in your app settings.py
and do not use the default of the plugin:

.. list-table:: Title
   :widths: 25 25 25 25
   :header-rows: 1

   * - ``APP_DIR``
     - $root
     - Base directory for storing secrets and cache. Defaults to the root of the module installation (recommended to change)
     - ``os.path.dirname(os.path.abspath(__file__))``
   * - ``SHELVE_SECRET_KEY``
     - None
     - Secret key for shelve (if ``STORAGE_BACKEND`` set to "shelve" (will be generated if not found)
     - fgayudsiushfdsfdf
   * - ``JWT_SECRET_KEY``
     - None
     - Secret key for json web tokens (if authentication enabled, and will be generated if not found)
     - fgayudsiushfdsfdf


The following additonal settings are available to set in your ``settings.py``:


.. list-table:: Title
   :widths: 25 25 25 25
   :header-rows: 1

   * - Name
     - Default
     - Description
     - Example
   * - ``URL_PREFIX``
     - api
     - The api prefix to use for the endpoint
     - river
   * - ``STORAGE_BACKEND``
     - shelve
     - The storage backend to use, either shelve or redis (requires redis setup)
     - redis
   * - ``REDIS_DB``
     - river-redis
     - The redis database name, only used if ``STORAGE_BACKEND`` is set to redis
     - another-name
   * - ``REDIS_HOST``
     - localhost
     - The redis host name, only used if ``STORAGE_BACKEND`` is set to redis
     - redis-container
   * - ``REDIS_PORT``
     - 6379
     - The redis port, only used if ``STORAGE_BACKEND`` is set to redis
     - 1111
   * - ``CACHE_DIR``
     - None (and then is set to ``os.path.join(APP_DIR, "cache")``)
     - The cache directory for tokens, recommended to set a custom ``APP_DIR`` and it will be a sub-directory ``cache`` there
     - /opt/cache
   * - ``DISABLE_AUTHENTICATION``
     - False
     - For views that require authentication, disable them.
     - True
   * - ``DOMAIN_URL``
     - http://127.0.0.1:8000
     - Domain used in templates, and api prefix
     - https://ml-server
   * - ``SESSION_EXPIRES_SECONDS``
     - 600
     - The number of seconds a session (upload request) is valid (10 minutes)
     - 6000
   * - ``TOKEN_EXPIRES_SECONDS``
     - 600
     - The number of seconds a token is valid (10 minutes)
     - 6000
   * - ``VIEW_RATE_LIMIT``
     - 10000/1day
     - View rate limit using django-ratelimit based on ipaddress
     - 100/1day
   * - ``VIEW_RATE_LIMIT_BLOCK``
     - True
     - Given that someone goes over, are they blocked for a period?
     - False


For more advanced settings like customizing the endpoints with authentication, see
the `settings.py <https://github.com/vsoch/django-river-ml/blob/main/django_river_ml/settings.py>`_ in the application.


Sample Application
------------------

An `example app <https://github.com/vsoch/django-river-ml/tree/main/tests>`_ is provided that
you can use to test. Once you have your environment setup, you can do:


.. code-block:: console

    $ python manage.py makemigrations
    $ python manage.py migrate
    $ python manage.py runserver
    

In another terminal, you can then run a sample script:

    
.. code-block:: bash

    $ python examples/regression/run.py
    $ python examples/binary/run.py


This library is under development and we will have more endpoints and functionality
coming soon!
