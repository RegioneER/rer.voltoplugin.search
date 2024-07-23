# -*- coding: utf-8 -*-
from rer.volto.search import _
from rer.volto.search.interfaces import IRERSearchCustomFilters
from zope.component import adapter
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface


@adapter(Interface, Interface)
@implementer(IRERSearchCustomFilters)
class EventsAdapter(object):
    """ """

    label = _("event_adapter_label", default="Events")

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return {
            "start": {
                "type": "date",
                "label": translate(
                    _("filter_start_label", default="Start date"),
                    context=self.request,
                ),
            },
            "end": {
                "type": "date",
                "label": translate(
                    _("filter_end_label", default="End date"),
                    context=self.request,
                ),
            },
        }
