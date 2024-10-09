from copy import deepcopy
from plone import api
from plone.api.exc import InvalidParameterError
from plone.base.interfaces.controlpanel import ISiteSchema
from plone.registry.interfaces import IRegistry
from plone.restapi.search.handler import SearchHandler
from plone.restapi.services import Service
from rer.voltoplugin.search import _
from rer.voltoplugin.search.interfaces import IRERSearchMarker
from rer.voltoplugin.search.restapi.utils import filter_query_for_search
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
        query = filter_query_for_search()

        if not query.keys():
            return {
                "@id": "http://localhost:8080/Plone/++api++/@rer-search?group=notizie",
                "facets": [],
                "items": [],
                "items_total": 0,
            }

        if self.solr_search_enabled:
            data = self.do_solr_search(query=query)
        else:
            query["use_site_search_settings"] = True
            data = SearchHandler(self.context, self.request).search(query)

        path_infos = self.get_path_infos(query=query)
        if path_infos:
            data["path_infos"] = path_infos
        return data

    def do_solr_search(self, query):
        query["facets"] = True
        query["facet_fields"] = ["site_name"]

        if not query.get("site_name", []):
            query["site_name"] = get_site_title()
        elif "all_sites" in query.get("site_name", []):
            del query["site_name"]

        facets = get_facets_data()
        for facets_mapping in facets:
            index_name = facets_mapping.get("index", "")
            if index_name == "group":
                query["facet_fields"].append("portal_type")
            else:
                query["facet_fields"].append(index_name)
        if "metadata_fields" not in query:
            query["metadata_fields"] = ["Description"]
        else:
            if not isinstance(query["metadata_fields"], list):
                query["metadata_fields"] = [query["metadata_fields"]]
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
            if facet_mapping.get("type", "") == "DateIndex":
                # skip it, we need to set some dates in the interface
                continue
            index_name = facet_mapping.get("index", "")
            # if index_name == "group":
            #     index_name = "portal_type"
            index_facets = solr_facets_data.get(index_name, [])
            # convert it into a dict, to better iterate
            index_facets = {k: v for d in index_facets for k, v in d.items()}

            if not index_facets:
                continue
            if index_name in ["site_name", "group"]:
                continue
            facet_mapping["items"] = [
                {"label": f"{k} ({v})", "value": k} for k, v in index_facets.items()
            ]

        self.handle_groups_facet(query=query, data=data, facets=new_facets)
        self.handle_sites_facet(query=query, data=data, facets=new_facets)
        return new_facets

    def handle_groups_facet(self, query, data, facets):
        if query.get("portal_type", None):
            # we need to do an additional query in solr, to get the results
            # unfiltered by portal_types
            new_query = deepcopy(query)
            del new_query["portal_type"]

            # simplify returned result data
            new_query["facet_fields"] = ["portal_type"]
            new_query["metadata_fields"] = ["UID"]
            new_data = SolrSearchHandler(self.context, self.request).search(new_query)
            types_facets = new_data["facets"]["portal_type"]
        else:
            types_facets = data["facets"]["portal_type"]

        # convert it into a dict, to better iterate
        types_facets = {k: v for d in types_facets for k, v in d.items()}

        for facet_mapping in facets:
            if facet_mapping.get("index", "") != "group":
                continue
            for type_data in facet_mapping.get("items", []):
                if type_data.get("id", "") == "all":
                    counter = sum(v for k, v in types_facets.items())
                else:
                    portal_types = type_data.get("portal_types", [])
                    counter = sum(
                        v for k, v in types_facets.items() if k in portal_types
                    )
                for lang, label in type_data.get("label", {}).items():
                    type_data["label"][lang] = f"{label} ({counter})"

    def handle_sites_facet(self, query, data, facets):
        """
        create site_name facets and append it on top
        """
        if query.get("site_name", None):
            # we need to do an additional query in solr, to get the results
            # unfiltered by site_name
            new_query = deepcopy(query)
            del new_query["site_name"]

            # simplify returned result data
            new_query["facet_fields"] = ["site_name"]
            new_query["metadata_fields"] = ["UID"]
            new_data = SolrSearchHandler(self.context, self.request).search(new_query)
            sites = new_data["facets"]["site_name"]
        else:
            sites = data["facets"]["site_name"]

        # convert it into a dict, to better iterate
        sites = {k: v for d in sites for k, v in d.items()}

        site_title = get_site_title()
        all_count = sum(v for k, v in sites.items())
        current_count = sum(v for k, v in sites.items() if k == site_title)

        labels = {}
        all_labels = {}
        current_site_labels = {}
        registry = getUtility(IRegistry)
        for lang in registry["plone.available_languages"]:
            all_labels[lang] = api.portal.translate(
                _(
                    "all_sites_label",
                    default="All Regione Emilia-Romagna sites (${count})",
                    mapping={"count": all_count},
                ),
                lang=lang,
            )
            current_site_labels[lang] = api.portal.translate(
                _(
                    "current_site_label",
                    default="In current website (${count})",
                    mapping={"count": current_count},
                ),
                lang=lang,
            )
            labels[lang] = api.portal.translate(
                _("where_label", default="Where"), lang=lang
            )

        all_facets = {"id": "all_sites", "label": all_labels}
        current_site_facets = {
            "id": site_title,
            "label": current_site_labels,
        }
        # now that we have
        sites_facets = {
            "index": "site_name",
            "items": [all_facets, current_site_facets],
            "type": "SiteName",
            "label": labels,
        }
        facets.insert(0, sites_facets)

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
