from plone.restapi.services import Service
from rer.voltoplugin.search.restapi.utils import get_indexes_mapping
from rer.voltoplugin.search.restapi.utils import get_types_groups
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class SearchFiltersGet(Service):
    def reply(self):
        params = {
            "groups": get_types_groups(),
            "indexes": get_indexes_mapping(),
        }

        return {"facets": params}
