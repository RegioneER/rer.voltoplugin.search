from plone import api
from plone.indexer.interfaces import IIndexableObject
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.catalog import (
    LazyCatalogResultSerializer as BaseSerializer,
)
from rer.voltoplugin.search.interfaces import IRERSearchMarker
from rer.voltoplugin.search.restapi.utils import filter_query_for_search
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
        """
        generate facets data
        """
        pc = api.portal.get_tool(name="portal_catalog")

        facets = get_facets_data()

        self.update_portal_type_facet(facets=facets)

        counters = {}
        for brain in brains:
            for facet in facets:
                index_id = facet.get("index", "")
                index_type = facet.get("type", "")

                if index_id in ["group"]:
                    # special handle
                    continue

                if index_type == "DateIndex":
                    # skip it, we need to set some dates in the interface
                    continue
                if index_id not in counters:
                    counters[index_id] = {}

                # get metadata/field value
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
                        if single_value not in counters[index_id]:
                            counters[index_id][single_value] = 1
                        else:
                            counters[index_id][single_value] += 1
                else:
                    if value not in counters[index_id]:
                        counters[index_id][value] = 1
                    else:
                        counters[index_id][value] += 1

        # now populate labels
        for facet in facets:
            index_id = facet.get("index", "")

            if index_id in ["group"]:
                continue

            if index_id not in counters:
                continue
            facet_values = sorted(
                [
                    {"label": f"{k} ({v})", "value": k}
                    for k, v in counters[index_id].items()
                ],
                key=lambda x: x["value"],
            )
            facet["items"] = facet_values
        return facets

    def update_portal_type_facet(self, facets):
        """
        We need to have the right count for groups facets because these are
        not proper facets, and the number of results should be the same also
        if we select a different group (groups only needs to show grouped
        information, not to filter).
        If we are filtering by type, this means that we need to do an another
        catalog search for get the proper counters for each group.
        """
        facet = [x for x in facets if x.get("index", "") == "group"][0]

        query = filter_query_for_search(fix_path=True)

        if "portal_type" in query:
            # remove types filter because we need to have total count in groups
            del query["portal_type"]

        portal_catalog = api.portal.get_tool(name="portal_catalog")
        brains_to_iterate = portal_catalog(**query)

        # count occurrences
        counters = {"all": 0}
        for brain in brains_to_iterate:
            for type_data in facet.get("items", []):
                group_id = type_data.get("id", "")
                if group_id == "all":
                    counters["all"] += 1
                else:
                    if brain.portal_type in type_data.get("portal_types", []):
                        if group_id not in counters:
                            counters[group_id] = 0
                        counters[group_id] += 1
        # update labels for each group with counters
        for type_data in facet.get("items", []):
            group_id = type_data.get("id", "")
            counter = counters.get(group_id, 0)
            for lang, label in type_data.get("label", {}).items():
                type_data["label"][lang] = f"{label} ({counter})"
        return facet
