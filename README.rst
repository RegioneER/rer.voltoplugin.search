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

If `rer.solrpush`__ is installed and active, the search will be done through SOLR and not Plone catalog.

In results facets there will be also a **site_name** additional data.

__ https://github.com/RegioneER/rer.solrpush


@rer-search endpoint
====================

This endpoint is similar to the original *@search* one but add an additional information about facets based on this package's settings and results.

facets is a list of filters that can be used to refine the search, and can be configured in the controlpanel.

The first one is always **portal_type**, followed by the indexes selected in controlpanel.


Example of @rer-search response::

    {
        "@id": "http://localhost:8080/Plone/++api++/@rer-search?SearchableText=foo",
        "facets": [
            {
                "index": "group",
                "items": [
                    {
                        "id": "all",
                        "items": {},
                        "label": {
                            "it": "Tutti i contenuti (5)"
                        }
                    },
                    {
                        "advanced_filters": {},
                        "icon": "",
                        "id": "pagine",
                        "label": {
                            "en": "Documents (1)",
                            "it": "Pagine (1)"
                        },
                        "portal_types": [
                            "Document"
                        ]
                    },
                    {
                        "advanced_filters": {},
                        "icon": "",
                        "id": "notizie",
                        "label": {
                            "en": "News (2)",
                            "it": "Notizie (2)"
                        },
                        "portal_types": [
                            "News Item",
                            "ExternalNews"
                        ]
                    },
                    {
                        "advanced_filters": {},
                        "icon": "",
                        "id": "bandi",
                        "label": {
                            "en": "Announcements (1)",
                            "it": "Bandi (1)"
                        },
                        "portal_types": [
                            "Bando"
                        ]
                    },
                    {
                        "advanced_filters": {},
                        "icon": "",
                        "id": "file-e-immagini",
                        "label": {
                            "en": "Files and images (0)",
                            "it": "File e immagini (0)"
                        },
                        "portal_types": [
                            "File",
                            "Image"
                        ]
                    },
                    {
                        "advanced_filters": [
                            {
                                "index_end": "end",
                                "index_start": "start",
                                "label_end": {
                                    "it": "Data di fine"
                                },
                                "label_start": {
                                    "it": "Data di inizio"
                                },
                                "type": "DateRangeIndex"
                            }
                        ],
                        "icon": "",
                        "id": "eventi",
                        "label": {
                            "en": "Events (1)",
                            "it": "Eventi (1)"
                        },
                        "portal_types": [
                            "Event"
                        ]
                    }
                ],
                "label": {
                    "it": "Cosa"
                },
                "type": "Groups"
            },
            {
                "index": "Subject",
                "items": [
                    {
                        "label": "aaa (2)",
                        "value": "aaa"
                    },
                    {
                        "label": "bbb (1)",
                        "value": "bbb"
                    }
                ],
                "label": {
                    "en": "Keywords",
                    "it": "Parole chiave"
                },
                "type": "KeywordIndex"
            }
        ],
        "items": [
            {
                "@id": "http://localhost:8080/Plone/xxx",
                "@type": "Document",
                "UID": "33fe109d445d4e1db4b46afae8301950",
                "description": "",
                "id": "xxx",
                "image_field": "",
                "image_scales": null,
                "review_state": "published",
                "title": "Pagina foo",
                "type_title": "Pagina"
            },
            ...
        ],
        "items_total": 5
    }

Advanced filters for groups
===========================

In each group types you can select an advanced filter.

Advanced filters are a list of preset filters that allow to add some extra filters when that group is selected in search.

By default there is only one advanced filter called "Events" that add start and end date filters, but you can add more
presets in your custom package.

Register new advanced filters
-----------------------------

Advanced filters are a list of named adapters, so you can add more and override existing ones if needed.

You just need to register a new named adapter::

    <adapter
      factory = ".my_filters.MyNewFilters"
      name= "my-filters"
    />

The adapter should have a `label` attribute (needed to show a human-readable name in sitesearch-settings view) and 
return the schema for the additional indexes::

    from zope.component import adapter
    from zope.interface import implementer
    from rer.voltoplugin.search.interfaces import IRERVoltopluginSearchCustomFilters
    from zope.interface import Interface
    from my.package import _
    from zope.i18n import translate


    @adapter(Interface, Interface)
    @implementer(IRERVoltopluginSearchCustomFilters)
    class MyNewFilters(object):
    """
    """

    label = _("some_labelid", default=u"Additional filters")

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return [
            {
                "index": "xxx",
                "items": {},
                "label": {"it": "Inizio", "en": "Start"},
                "type": "DateIndex",
            },
            {
                "index": "yyy",
                "items": {},
                "label": {"it": "Fine", "en": "End"},
                "type": "DateIndex",
            },
        ]

Where `xxx` and `yyy` are Plone's catalog indexes.

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

Credits
=======

Developed with the support of

.. image:: http://www.regione.emilia-romagna.it/rer.gif
   :alt: Regione Emilia-Romagna
   :target: http://www.regione.emilia-romagna.it/

Regione Emilia Romagna supports the `PloneGov initiative`__.

__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: https://avatars1.githubusercontent.com/u/1087171?s=100&v=4
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.net/
