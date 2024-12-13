from copy import deepcopy
from DateTime import DateTime
from plone import api
from plone.i18n.normalizer import idnormalizer
from plone.registry.interfaces import IRegistry
from plone.restapi.search.utils import unflatten_dotted_dict
from Products.DateRecurringIndex.index import DateRecurringIndex
from rer.voltoplugin.search import _
from rer.voltoplugin.search.interfaces import IRERVoltopluginSearchCustomFilters
from rer.voltoplugin.search.interfaces import IRERVoltopluginSearchCustomQuery
from rer.voltoplugin.search.interfaces import IRERVoltopluginSearchSettings
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import subscribers
from zope.globalrequest import getRequest

import json
import logging


logger = logging.getLogger(__name__)


def get_value_from_registry(field):
    try:
        data = api.portal.get_registry_record(
            field, interface=IRERVoltopluginSearchSettings
        )
        if data:
            return json.loads(data)
        return {}
    except KeyError:
        return {}


def get_facets_data():
    facets = []
    pc = api.portal.get_tool(name="portal_catalog")
    # first of all: portal_type
    registry = getUtility(IRegistry)
    what_labels = {}
    for lang in registry["plone.available_languages"]:
        what_labels[lang] = api.portal.translate(
            _("what_label", default="What"), lang=lang
        )

    portal_type_data = {
        "label": what_labels,
        "items": get_types_group_mapping(),
        "index": "group",
        "type": "Groups",  # custom name needed in frontend
    }
    facets.append(portal_type_data)

    # then other indexes
    indexes_mapping = get_value_from_registry(field="available_indexes") or []
    for index_mapping in indexes_mapping:
        index_id = index_mapping.get("index", "")
        facets.append(
            {
                "label": index_mapping.get("label", index_id),
                "index": index_id,
                "type": pc.Indexes[index_id].__class__.__name__,
                "items": {},
            }
        )
    return facets


def get_types_group_mapping():
    all_labels = {}

    registry = getUtility(IRegistry)

    for lang in registry["plone.available_languages"]:
        all_labels[lang] = api.portal.translate(
            _("all_types_label", default="All content types"), lang=lang
        )

    res = [{"label": all_labels, "items": {}, "id": "all"}]

    types_grouping = get_value_from_registry(field="types_grouping")
    if not types_grouping:
        return res
    for types_group in types_grouping:
        label = types_group.get("label", {})
        current_lang = api.portal.get_current_language()
        current_label = label.get(current_lang, "it")
        group_id = idnormalizer.normalize(current_label)
        res.append(
            {
                "label": types_group.get("label", {}),
                "portal_types": types_group.get("portal_type", []),
                "advanced_filters": expand_advanced_filters(
                    name=types_group.get("advanced_filters", "")
                ),
                "icon": types_group.get("icon", ""),
                "id": group_id,
            }
        )
    return res


def expand_advanced_filters(name):
    if not name:
        return {}
    request = getRequest()
    portal = api.portal.get()
    try:
        filters_adapter = getMultiAdapter(
            (portal, request),
            IRERVoltopluginSearchCustomFilters,
            name=name,
        )
        return filters_adapter()
    except ComponentLookupError as e:
        logger.exception(e)
        return {}


def filter_query_for_search(fix_path=False):
    """
    Fix query parameters
    fix_path is a flag that is used to append site id to the queried path.
    It is optional because when we use SearchHandler in @search endpoint, there
    is already a method to fix path in query
    """
    request = getRequest()
    query = deepcopy(request.form)
    query = unflatten_dotted_dict(query)
    plone_utils = api.portal.get_tool(name="plone_utils")
    pc = api.portal.get_tool(name="portal_catalog")

    if "group" in query:
        group_value = query.get("group", "")
        for mapping in get_facets_data()[0].get("items", []):
            if mapping.get("id", "") == group_value:
                portal_types = mapping.get("portal_types", [])
                if portal_types:
                    if not isinstance(portal_types, list):
                        portal_types = [portal_types]
                    query["portal_type"] = plone_utils.getUserFriendlyTypes(
                        portal_types
                    )
        del query["group"]

    for key, value in query.items():
        if value in ["false", "False"]:
            query[key] = False
        if value in ["true", "True"]:
            query[key] = True

        if isinstance(pc.Indexes.get(key, None), DateRecurringIndex):
            # convert strings into a DateTime object
            if isinstance(value.get("query", ""), list):
                query[key]["query"] = [DateTime(x) for x in value["query"]]
            else:
                query[key]["query"] = DateTime(value["query"])

        if key == "path" and fix_path:
            portal_path = "/".join(api.portal.get().getPhysicalPath())
            if not value.get("query", "").startswith(portal_path):
                query[key]["query"] = f"{portal_path}{value['query']}"
    for index in ["metadata_fields"]:
        if index in query:
            del query[index]

    # check if there are some adapters that fix query
    handlers = subscribers(
        (api.portal.get(), request), IRERVoltopluginSearchCustomQuery
    )
    for handler in sorted(handlers, key=lambda h: h.order):
        query = handler(query=query)
    return query
