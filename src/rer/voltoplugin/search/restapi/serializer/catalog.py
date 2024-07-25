from copy import deepcopy
from plone import api
from plone.indexer.interfaces import IIndexableObject
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.serializer.catalog import (
    LazyCatalogResultSerializer as BaseSerializer,
)
from rer.voltoplugin.search.interfaces import IRERSearchMarker
from rer.voltoplugin.search.restapi.utils import get_facets_data
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from ZTUtils.Lazy import Lazy

import Missing


@implementer(ISerializeToJson)
@adapter(Lazy, IRERSearchMarker)
class LazyCatalogResultSerializer(BaseSerializer):
    def __call__(self, fullobjects=False):
        data = super().__call__(fullobjects=fullobjects)
        # add facets information
        data.update({"facets": self.extract_facets(brains=self.lazy_resultset)})
        return data

    def extract_facets(self, brains):
        pc = api.portal.get_tool(name="portal_catalog")

        facets = get_facets_data()

        self.update_portal_type_facet(facet=facets[0])

        for brain in brains:
            for facet in facets:
                index_id = facet.get("index", "")
                index_type = facet.get("type", "")

                if index_id == "portal_type":
                    # special handle
                    continue

                if index_type == "DateIndex":
                    # skip it, we need to set some dates in the interface
                    continue
                try:
                    value = getattr(brain, index_id)
                except AttributeError:
                    # index is not a brain's metadata. Load item object
                    # (could be painful)
                    item = brain.getObject()
                    type_adapter = queryMultiAdapter((item, pc), IIndexableObject)
                    value = getattr(type_adapter, index_id, None)
                if not value or value == Missing.Value:
                    if not isinstance(value, bool) and not isinstance(value, int):
                        # bool and numbers can be False or 0
                        continue
                if isinstance(value, list) or isinstance(value, tuple):
                    for single_value in value:
                        if single_value not in facet["items"]:
                            facet["items"][single_value] = 1
                        else:
                            facet["items"][single_value] += 1
                else:
                    if value not in facet["items"][single_value]:
                        facet["items"][single_value][value] = 1
                    else:
                        facet["items"][single_value][value] += 1
        return facets

    def update_portal_type_facet(self, facet):
        """
        We need to have the right count for groups facets because these are
        not proper facets, and the number of results should be the same also
        if we select a different group (groups only needs to show grouped
        information, not to filter).
        If we are filtering by type, this means that we need to do an another
        catalog search for get the proper counters for each group.
        """
        query = deepcopy(self.request.form)
        query = unflatten_dotted_dict(query)

        for key, value in query.items():
            if value in ["false", "False"]:
                query[key] = False
            if value in ["true", "True"]:
                query[key] = True

        for index in ["metadata_fields", "portal_type"]:
            if index in query:
                del query[index]

        # fix portal types
        types = query.get("portal_type", [])
        if "query" in types:
            types = types["query"]
        query["portal_type"] = self.filter_types(types)

        portal_catalog = api.portal.get_tool(name="portal_catalog")
        brains_to_iterate = portal_catalog(**query)
        for brain in brains_to_iterate:
            for type_data in facet.get("items", []):
                if type_data.get("id", "") == "all":
                    # all
                    type_data["items"][brain.portal_type] = 1
                else:
                    if brain.portal_type in type_data.get("items", {}):
                        type_data["items"][brain.portal_type] += 1
        return facet

    def filter_types(self, types):
        """
        Search only in enabled types in control-panel
        """
        plone_utils = api.portal.get_tool(name="plone_utils")
        if not isinstance(types, list):
            types = [types]
        return plone_utils.getUserFriendlyTypes(types)
