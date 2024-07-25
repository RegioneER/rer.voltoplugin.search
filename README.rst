.. This README is meant for consumption by humans and PyPI. PyPI can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on PyPI or github. It is a comment.

.. image:: https://github.com/collective/rer.voltoplugin.search/actions/workflows/plone-package.yml/badge.svg
    :target: https://github.com/collective/rer.voltoplugin.search/actions/workflows/plone-package.yml

.. image:: https://coveralls.io/repos/github/collective/rer.voltoplugin.search/badge.svg?branch=main
    :target: https://coveralls.io/github/collective/rer.voltoplugin.search?branch=main
    :alt: Coveralls

.. image:: https://codecov.io/gh/collective/rer.voltoplugin.search/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/collective/rer.voltoplugin.search

.. image:: https://img.shields.io/pypi/v/rer.voltoplugin.search.svg
    :target: https://pypi.python.org/pypi/rer.voltoplugin.search/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/rer.voltoplugin.search.svg
    :target: https://pypi.python.org/pypi/rer.voltoplugin.search
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/rer.voltoplugin.search.svg?style=plastic   :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/rer.voltoplugin.search.svg
    :target: https://pypi.python.org/pypi/rer.voltoplugin.search/
    :alt: License

.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

======================
RER Voltoplugin Search
======================

Add-on for manage Search results in Volto.

Features
========

- Control panel in plone registry to manage Search settings.
- Restapi endpoint that exposes these settings for Volto.

Vocabularies
============

rer.voltoplugin.search.vocabularies.AdvancedFiltersVocabulary
-------------------------------------------------------------

Vocabulary that returns the list of registered adapters for custom filters based on content-types.


rer.voltoplugin.search.vocabularies.IndexesVocabulary
-----------------------------------------------------

Vocabulary that returns the list of available indexes in portal_catalog.


rer.voltoplugin.search.vocabularies.GroupingTypesVocabulary
-----------------------------------------------------------

Vocabulary that returns the list of available portal_types.

If rer.solr is installed, returns the list of portal_types indexed in SOLR, otherwise return ReallyUserFriendlyTypes Plone vocabulary.


Volto integration
=================

To use this product in Volto, your Volto project needs to include a new plugin: https://github.com/collective/XXX


Translations
============

This product has been translated into

- Italian



Installation
============

Install rer.voltoplugin.search by adding it to your buildout::

    [buildout]

    ...

    eggs =
        rer.voltoplugin.search


and then running ``bin/buildout``


Contribute
==========

- Issue Tracker: https://github.com/collective/rer.voltoplugin.search/issues
- Source Code: https://github.com/collective/rer.voltoplugin.search


License
=======

The project is licensed under the GPLv2.
