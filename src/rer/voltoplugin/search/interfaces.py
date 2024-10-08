from plone.restapi.controlpanels import IControlpanel
from plone.supermodel import model
from rer.voltoplugin.search import _
from zope import schema
from zope.interface import Attribute
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import json


class IRERVoltopluginSearchControlpanel(IControlpanel):
    """Marker interface"""


class IRERVoltopluginSearchLayer(IDefaultBrowserLayer):
    """A layer specific for rer.voltoplugin.search"""


class IRERVoltopluginSearchCustomFilters(Interface):
    """Marker interface"""

    label = Attribute("The label shown in the select")

    def __init__(context, request):
        """Adapts context and the request."""

    def __call__():
        """ """


class IRERVoltopluginSearchCustomQuery(Interface):
    """Marker interface"""

    def __init__(context, request):
        """Adapts context and the request."""

    def __call__(query):
        """ """


class IRERSearchMarker(Interface):
    """
    Marker interface
    """


class IRERVoltopluginSearchSettings(model.Schema):
    """ """

    max_word_len = schema.Int(
        title=_("Maximum number of characters in a single word"),
        description=_(
            "help_max_word_len",
            default="Set what is the maximum length of a single search word. "
            "Longer words will be omitted from the search.",
        ),
        default=128,
        required=False,
    )

    max_words = schema.Int(
        title=_("Maximum number of words in search query"),
        description=_(
            "help_max_words",
            default="Set what is the maximum number of words in the search "
            "query. The other words will be omitted from the search.",
        ),
        default=32,
        required=False,
    )

    types_grouping = schema.SourceText(
        title=_("types_grouping_label", default="Types grouping"),
        description=_(
            "types_grouping_help",
            default="If you fill this field, you can group search results by "
            "content-types.",
        ),
        required=False,
        default=json.dumps(
            [
                {
                    "label": {"it": "Pagine", "en": "Documents"},
                    "portal_type": ["Document"],
                },
                {
                    "label": {"it": "Notizie", "en": "News"},
                    "portal_type": ["News Item", "ExternalNews"],
                },
                {
                    "label": {"it": "Bandi", "en": "Announcements"},
                    "portal_type": ["Bando"],
                },
                {
                    "label": {"it": "File e immagini", "en": "Files and images"},
                    "portal_type": ["File", "Image"],
                },
                {
                    "label": {"it": "Eventi", "en": "Events"},
                    "portal_type": ["Event"],
                    "advanced_filters": "events",
                },
            ]
        ),
    )

    available_indexes = schema.SourceText(
        title=_("available_indexes_label", default="Available indexes"),
        description=_(
            "available_indexes_help",
            default="Select which additional filters to show in the column.",
        ),
        required=False,
        default=json.dumps(
            [
                {
                    "label": {"it": "Parole chiave", "en": "Keywords"},
                    "index": "Subject",
                },
            ]
        ),
    )
