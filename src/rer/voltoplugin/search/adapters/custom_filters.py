from plone import api
from plone.registry.interfaces import IRegistry
from rer.voltoplugin.search import _
from rer.voltoplugin.search.interfaces import IRERVoltopluginSearchCustomFilters
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface


@adapter(Interface, Interface)
@implementer(IRERVoltopluginSearchCustomFilters)
class EventsAdapter:
    """ """

    label = _("event_adapter_label", default="Events")

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        registry = getUtility(IRegistry)
        start_labels = {}
        end_labels = {}
        labels = {}
        for lang in registry["plone.available_languages"]:
            start_labels[lang] = api.portal.translate(
                _("filter_start_label", default="Start date"), lang=lang
            )
            end_labels[lang] = api.portal.translate(
                _("filter_end_label", default="End date"), lang=lang
            )
            labels[lang] = api.portal.translate(
                _("filter_event_dates_label", default="Event date"), lang=lang
            )
        return [
            {
                "index_start": "start",
                "index_end": "end",
                "label": labels,
                "label_start": start_labels,
                "label_end": end_labels,
                "type": "DateRangeIndex",
            },
        ]
