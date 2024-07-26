from plone import api
from plone.i18n.normalizer import idnormalizer
from plone.registry.interfaces import IRegistry
from plone.restapi.search.utils import unflatten_dotted_dict
from rer.voltoplugin.search import _
from rer.voltoplugin.search.interfaces import IRERVoltopluginSearchCustomFilters
from rer.voltoplugin.search.interfaces import IRERVoltopluginSearchSettings
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import getUtility
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
    request = getRequest()
    query = unflatten_dotted_dict(request)
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
        "index": "portal_type",
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

    # at least, append advanced_filters, if set and remove unused data
    group = query.get("group", "")
    for group_data in facets[0]["items"]:
        advanced_filters = group_data.get("advanced_filters", {})
        if group and group_data.get("id") == group and advanced_filters:
            facets.extend(advanced_filters)
        if "advanced_filters" in group_data:
            del group_data["advanced_filters"]
    return facets


def get_types_group_mapping():
    all_labels = {}

    registry = getUtility(IRegistry)

    for lang in registry["plone.available_languages"]:
        all_labels[lang] = api.portal.translate(
            _("all_types_label", default="All content types"), lang=lang
        )

    res = [{"index": "portal_type", "label": all_labels, "items": {}, "id": "all"}]

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
                "items": {x: 0 for x in types_group.get("portal_type", [])},
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
    except ComponentLookupError:
        return {}
