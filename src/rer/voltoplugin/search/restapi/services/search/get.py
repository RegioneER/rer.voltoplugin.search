from copy import deepcopy
from plone import api
from plone.api.exc import InvalidParameterError
from plone.base.interfaces.controlpanel import ISiteSchema
from plone.registry.interfaces import IRegistry
from plone.restapi.search.handler import SearchHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services import Service
from rer.voltoplugin.search.interfaces import IRERSearchMarker
from rer.voltoplugin.search.restapi.utils import get_facets_data
from zope.component import getUtility
from zope.interface import alsoProvides


try:
    from rer.solrpush.interfaces.settings import IRerSolrpushSettings
    from rer.solrpush.restapi.services.solr_search.solr_search_handler import (
        SolrSearchHandler,
    )
    from rer.solrpush.utils.solr_indexer import get_site_title

    HAS_SOLR = True
except ImportError:
    HAS_SOLR = False


import six


class SearchGet(Service):
    @property
    def solr_search_enabled(self):
        if not HAS_SOLR:
            return False
        try:
            active = api.portal.get_registry_record(
                "active", interface=IRerSolrpushSettings
            )
            search_enabled = api.portal.get_registry_record(
                "search_enabled", interface=IRerSolrpushSettings
            )
            return active and search_enabled
        except (KeyError, InvalidParameterError):
            return False

    def reply(self):
        # mark request with custom layer to be able to override catalog serializer and add facets
        alsoProvides(self.request, IRERSearchMarker)

        query = deepcopy(self.request.form)
        query = unflatten_dotted_dict(query)
        path_infos = self.get_path_infos(query=query)

        if not query.get("SearchableText", ""):
            return {
                "@id": "http://localhost:8080/Plone/++api++/@rer-search?group=notizie",
                "facets": [],
                "items": [],
                "items_total": 0,
            }

        self.filter_types(query)
        if self.solr_search_enabled:
            data = self.do_solr_search(query=query)
        else:
            query["use_site_search_settings"] = True
            data = SearchHandler(self.context, self.request).search(query)
        if path_infos:
            data["path_infos"] = path_infos
        return data

    def filter_types(self, query):
        if "group" in query:
            group_value = query.get("group", "")
            for mapping in get_facets_data()[0].get("items", []):
                if mapping.get("id", "") == group_value:
                    if mapping.get("items", {}):
                        query["portal_type"] = list(mapping["items"].keys())
            del query["group"]
        return query

    def do_solr_search(self, query):
        query["facets"] = True
        query["facet_fields"] = ["site_name"]

        if not query.get("site_name", []):
            query["site_name"] = get_site_title()
        elif "all" in query.get("site_name", []):
            del query["site_name"]

        facets = get_facets_data()
        for facets_mapping in facets:
            query["facet_fields"].append(facets_mapping.get("index", ""))
        if "metadata_fields" not in query:
            query["metadata_fields"] = ["Description"]
        else:
            if "Description" not in query["metadata_fields"]:
                query["metadata_fields"].append("Description")
        data = SolrSearchHandler(self.context, self.request).search(query)
        data["facets"] = self.remap_solr_facets(data=data, query=query)
        data["current_site"] = get_site_title()
        return data

    def remap_solr_facets(self, data, query):
        new_facets = get_facets_data()
        solr_facets_data = data.get("facets", {})
        for facet_mapping in new_facets:
            index_name = facet_mapping.get("index", "")
            if facet_mapping.get("type", "") == "DateIndex":
                # skip it, we need to set some dates in the interface
                continue
            solr_facets = solr_facets_data.get(index_name, {})
            if not solr_facets:
                continue
            if index_name == "portal_type":
                # remap it into a dictionary
                solr_facets = {k: v for d in solr_facets for k, v in d.items()}
                for type_data in facet_mapping.get("items", []):
                    if type_data.get("id", "") == "all":
                        # all
                        type_data["items"] = solr_facets
                    else:
                        for type_name in type_data.get("items", {}).keys():
                            type_data["items"][type_name] = solr_facets.get(
                                type_name, 0
                            )
            elif index_name == "site_name":
                continue

            else:
                facet_mapping["items"] = solr_facets

        site_facets = self.handle_sites_facet(data=data, query=query)
        new_facets.insert(0, site_facets)

        return new_facets

    def handle_sites_facet(self, data, query):
        site = query.get("site_name", "")
        if site:
            # we need to do an additional query in solr, to get the results
            # unfiltered by site_name
            new_query = deepcopy(query)
            del new_query["site_name"]
            # simplify returned result data
            new_query["facet_fields"] = ["site_name"]
            new_query["metadata_fields"] = ["UID"]
            new_data = SolrSearchHandler(self.context, self.request).search(new_query)
            indexes = new_data["facets"]["site_name"]
        else:
            indexes = data["facets"]["site_name"]
        return indexes

    def get_path_infos(self, query):
        if "path" not in query:
            return {}
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)
        site_title = getattr(site_settings, "site_title") or ""
        if six.PY2:
            site_title = site_title.decode("utf-8")

        path = query["path"]
        if isinstance(path, dict):
            path = path.get("query", "")
        root_path = "/".join(api.portal.get().getPhysicalPath())

        data = {
            "site_name": site_title,
            "root": "/".join(api.portal.get().getPhysicalPath()),
        }
        if path != root_path:
            folder = api.content.get(path)
            if folder:
                data["path_title"] = folder.title
        return data


class SearchLocalGet(SearchGet):
    @property
    def solr_search_enabled(self):
        return False
