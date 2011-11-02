#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Setup the Keyring Lib for Python.
"""

import sys


setup_params = dict(
    name = 'keyring',
    version = "0.7",
    description = "Store and access your passwords safely.",
    url = "http://home.python-keyring.org/",
    keywords = "keyring Keychain GnomeKeyring Kwallet password storage",
    maintainer = "Kang Zhang",
    maintainer_email = "jobo.zh@gmail.com",
    license="PSF",
    long_description = open('README').read() + open('CHANGES.txt').read(),
    platforms = ["Many"],
    packages = ['keyring', 'keyring.tests', 'keyring.util',
                'keyring.backends'],
)

if sys.version_info >= (3,0):
    setup_params.update(
        use_2to3=True,
    )

if __name__ == '__main__':
    try:
        from setuptools import setup
    except ImportError:
        from distutils.core import setup
    setup(**setup_params)
