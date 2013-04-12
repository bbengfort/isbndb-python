#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Python API access library for isbndb.com',
    'author': 'Benjamin Bengfort',
    'url': 'https://github.com/bbengfort/isbndb-python/',
    'author_email': 'benjamin@bengfort.com',
    'version': '1.0.0',
    'install_requires': ['nose','python-dateutil',],
    'packages': ['isbndb',],
    'scripts': [],
    'name': 'isbndb-python',
}

setup(**config)
