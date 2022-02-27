# django-river-ml

[![CI](https://github.com/vsoch/django-river-ml/actions/workflows/main.yml/badge.svg)](https://github.com/vsoch/django-river-ml/actions/workflows/main.yml)
[![PyPI version](https://badge.fury.io/py/django-river-ml.svg)](https://badge.fury.io/py/django-river-ml)

Django models to deploy [river](https://riverml.xyz) online machine learning. 
This is a Django version of [chantilly](https://github.com/online-ml/chantilly) that aims to use the
same overall design. We also include [example clients](examples/) and a test application in [tests](tests).

See the ⭐️ [Documentation](https://vsoch.github.io/django-river-ml/) ⭐️ to get started!

## TODO

- tests
- should we have a server generic client to plug in here instead?
- do we want a spec? [issue](https://github.com/online-ml/river/issues/845)
- clean up docstrings -> docs and python docs -> envars list and how to define -> pretty docs
- implement more examples?
- add and test authenticated views
- do we want a default interface for something?
- upload to pypi and automated release after that
