from plone.restapi.controlpanels import IControlpanel
from plone.supermodel import model
from  import _
from zope import schema
from zope.interface import Attribute
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IRERVoltoSearchControlpanel(IControlpanel):
    """Marker interface"""


class IRERVoltoSearchLayer(IDefaultBrowserLayer):
    """A layer specific for """


class IRERVoltoSearchCustomFilters(Interface):
    """Marker interface"""

    label = Attribute("The label shown in the select")

    def __init__(context, request):
        """Adapts context and the request."""

    def __call__():
        """ """


class IRERVoltoSearchSettings(model.Schema):
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
    )

    available_indexes = schema.SourceText(
        title=_("available_indexes_label", default="Available indexes"),
        description=_(
            "available_indexes_help",
            default="Select which additional filters to show in the column.",
        ),
        required=False,
    )
