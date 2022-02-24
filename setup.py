#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


version = get_version("django_river_ml", "version.py")

with open("README.md") as fd:
    readme = fd.read()

setup(
    name="django-river-ml",
    version=version,
    description="Online machine learning with river and Django.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Vanessa Sochat",
    author_email="vsoch@users.noreply.github.io",
    url="https://github.com/vsoch/django-river-ml",
    packages=["django_river_ml"],
    include_package_data=True,
    install_requires=[
        "django",
        "djangorestframework",
        "django-ratelimit",
        "pyjwt",
        "river",
        "redis",
        "dill",
        "cerebrus",
    ],
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords="online-ml,river,chantilly",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
    ],
)
