# django-river-ml

[![PyPI version](https://badge.fury.io/py/django-river-ml.svg)](https://badge.fury.io/py/django-river-ml)

Django models to deploy [river](https://riverml.xyz) online machine learning. 
This is a Django version of [chantilly](https://github.com/online-ml/chantilly) that aims to use the
same overall design. We also include [example clients](examples/) and a test application in [tests](tests).

### How is it different?

This is a Django plugin, so it's more intended to be generalizable for your Django application.
Since we assume you will be using a relational database with some number of models (tables) and
online-ml works well with dictionaries, we use either [shelve](https://docs.python.org/3/library/shelve.html) (development) or redis (production)
to store models. The plugin here is different from chantilly in the following ways:

 - it's intended to be easily customized, so most configurables are exposed in settings customized by your app
 - we have added more kinds of model types (under development)
 - we require each new model to be added with a flavor, and data (metrics, stats, etc.) is stored relevant to that. The original chanilly puts everything under "metrics" or "stats" and then wipes the database if a new flavor is added.
 - a few additional API endpoints were added (also under development)

**under development** not ready to use yet! But should be with a few more evenings and the weekend :)

## Quickstart

### Install

Install django-river-ml (note that river can be troublesome with just pip needing
to compile numpy, etc., it's recommended to use conda and we will have a conda package soon).

```bash
conda create --name ml
conda activate ml
conda install river
pip install django-river-ml
```

or development from the code:

```bash
$ pip install -e .
```

Add it to your `INSTALLED_APPS` along with `rest_framework`

```python

    INSTALLED_APPS = (
        ...
        'django_river_ml',
        'rest_framework',
        ...
    )
```

Add django-river-ml's URL patterns:

```python

    from django_river_ml import urls as django_river_urls
    urlpatterns = [
        ...
        url(r'^', include(django_river_urls)),
        ...
    ]
```

See the [documentation](https://vsoch.github.io/django-river-ml/) or [getting started guide](https://vsoch.github.io/django-river-ml/docs/getting-started/) for more details about setup, and testing. 

### Sample Application

An [example application](tests) is provided that you can use. As above, install the module, then do:

```bash
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
```

In another terminal, you can then run a sample script:

```bash
python examples/regression/run.py
python examples/regression/run.py
```

## TODO

- ask if we should have a server generic client to plug in here instead?
- do we want a spec? [issue](https://github.com/online-ml/river/issues/845)
- clean up docstrings -> docs and python docs -> envars list and how to define -> pretty docs
- implement examples
- add and test authenticated views
- do we want a default interface for something?
- tests
- upload to pypi
