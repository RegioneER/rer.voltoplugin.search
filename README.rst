.. This README is meant for consumption by humans and PyPI. PyPI can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on PyPI or github. It is a comment.

.. image:: https://github.com/collective/rer.volto.search/actions/workflows/plone-package.yml/badge.svg
    :target: https://github.com/collective/rer.volto.search/actions/workflows/plone-package.yml

.. image:: https://coveralls.io/repos/github/collective/rer.volto.search/badge.svg?branch=main
    :target: https://coveralls.io/github/collective/rer.volto.search?branch=main
    :alt: Coveralls

.. image:: https://codecov.io/gh/collective/rer.volto.search/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/collective/rer.volto.search

.. image:: https://img.shields.io/pypi/v/rer.volto.search.svg
    :target: https://pypi.python.org/pypi/rer.volto.search/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/rer.volto.search.svg
    :target: https://pypi.python.org/pypi/rer.volto.search
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/rer.volto.search.svg?style=plastic   :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/rer.volto.search.svg
    :target: https://pypi.python.org/pypi/rer.volto.search/
    :alt: License

.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

================
RER Volto Search
================

Add-on for manage Search results in Volto.

Features
--------

- Control panel in plone registry to manage Search settings.
- Restapi endpoint that exposes these settings for Volto.

@gdpr-cookie-settings
---------------------

Anonymous users can't access registry resources by default with plone.restapi (there is a special permission).

To avoid enabling registry access to everyone, this package exposes a dedicated restapi route with GDPR cookie settings: *@gdpr-cookie-settings*::

    > curl -i http://localhost:8080/Plone/@gdpr-cookie-settings -H 'Accept: application/json' --user admin:admin


Volto integration
-----------------

To use this product in Volto, your Volto project needs to include a new plugin: https://github.com/collective/XXX


Translations
------------

This product has been translated into

- Italian



Installation
------------

Install rer.volto.search by adding it to your buildout::

    [buildout]

    ...

    eggs =
        rer.volto.search


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/collective/rer.volto.search/issues
- Source Code: https://github.com/collective/rer.volto.search


License
-------

The project is licensed under the GPLv2.
