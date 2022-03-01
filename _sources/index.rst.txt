.. _manual-main:

===============
Django River ML
===============

.. image:: https://img.shields.io/github/stars/vsoch/django-river-ml?style=social
    :alt: GitHub stars
    :target: https://github.com/vsoch/django-river-ml/stargazers


To see the code, head over to the `repository <https://github.com/vsoch/django-river-ml/>`_.

.. _main-getting-started:

------------------------------------
Getting started with Django River ML
------------------------------------

Django models to deploy `river <https://riverml.xyz>`_ online machine learning. 
This is a Django version of `chantilly <https://github.com/online-ml/chantilly>`_ that aims to use the
same overall design. We also include `example clients <https://github.com/vsoch/django-river-ml/tree/main/examples>`_ and a 
test application in `tests <https://github.com/vsoch/django-river-ml/tree/main/tests>`_. You can use
the Python `riverapi <https://github.com/vsoch/riverapi>`_ to interact with the server, which describes and
implements the client side of the `spec <https://vsoch.github.io/riverapi/getting_started/spec.html>`_ implemented on the server here.

How is it different?
--------------------

This is a Django plugin, so it's more intended to be generalizable for your Django application.
Since we assume you will be using a relational database with some number of models (tables) and
online-ml works well with dictionaries, we use either `shelve <https://docs.python.org/3/library/shelve.html)>`_ 
(development) or redis (production) to store models. The plugin here is different from chantilly in the following ways:

 - it's intended to be easily customized, so most configurables are exposed in settings customized by your app
 - we have added more kinds of model types (under development)
 - we require each new model to be added with a flavor, and data (metrics, stats, etc.) is stored relevant to that. The original chanilly puts everything under "metrics" or "stats" and then wipes the database if a new flavor is added.
 - a few additional API endpoints were added (also under development)
 - to remove the logic from the particular API implementation, we have a [client class](django_river_ml/client.py) that returns a boolean (success) and data result for each function.

**under development** not ready to use yet! But should be with a few more evenings and the weekend :)

.. _main-support:

-------
Support
-------

* For **bugs and feature requests**, please use the `issue tracker <https://github.com/vsoch/django-river-ml/issues>`_.
* For **contributions**, visit us on `Github <https://github.com/vsoch/django-river-ml>`_.

---------
Resources
---------

`GitHub Repository <https://github.com/vsoch/django-river-ml>`_
    The code on GitHub.

`river Documentation <https://riverml.xyz/latest/>`_
   The official river Documentation.

`riverapi Python client <https://github.com/vsoch/riverapi/>`_
    A python client intended to interact with a server like this one.

`riverapi specification <https://vsoch.github.io/riverapi/getting_started/spec.html>`_
   The specification for the server endpoints and client.
   

.. toctree::
   :caption: Getting started
   :name: getting_started
   :hidden:
   :maxdepth: 3

   getting_started/index
   getting_started/user-guide

.. toctree::
    :caption: API Reference
    :name: api-reference
    :hidden:
    :maxdepth: 1

    api_reference/django-river-ml
    api_reference/internal/modules
