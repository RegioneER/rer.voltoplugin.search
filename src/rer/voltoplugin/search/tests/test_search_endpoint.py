from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from rer.voltoplugin.search.testing import RESTAPI_TESTING
from transaction import commit

import unittest


class SearchTest(unittest.TestCase):
    layer = RESTAPI_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.url = "/@rer-search"

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # create some data

        self.news = api.content.create(
            container=self.portal,
            type="News Item",
            title="News foo",
            subject=("aaa", "bbb"),
        )
        self.document = api.content.create(
            container=self.portal,
            type="Document",
            title="Document foo",
            subject=("aaa"),
        )
        self.event = api.content.create(
            container=self.portal,
            type="Event",
            title="Event foo",
            subject=("bbb"),
        )

        self.folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder foo",
            subject=("aaa"),
        )
        commit()

    def tearDown(self):
        self.api_session.close()

    def test_if_not_pass_SearchableText_do_not_return_results(self):
        query = {}
        response = self.api_session.get(self.url, params=query)
        data = response.json()
        self.assertEqual(data["facets"], [])
        self.assertEqual(data["items"], [])
        self.assertEqual(data["items_total"], 0)

    def test_if_pass_SearchableText_return_results(self):
        query = {"SearchableText": "foo"}
        response = self.api_session.get(self.url, params=query)
        data = response.json()
        self.assertEqual(data["items_total"], 4)

    def test_return_default_facets_stored_in_registry(self):
        query = {"SearchableText": "foo"}
        response = self.api_session.get(self.url, params=query)
        data = response.json()
        self.assertEqual(
            data["facets"],
            [
                {
                    "index": "portal_type",
                    "items": [
                        {
                            "id": "all",
                            "index": "portal_type",
                            "items": {
                                "Document": 1,
                                "Event": 1,
                                "Folder": 1,
                                "News Item": 1,
                            },
                            "label": {"en": "All content types"},
                        },
                        {
                            "icon": "",
                            "id": "documents",
                            "items": {"Document": 1},
                            "label": {"en": "Documents", "it": "Pagine"},
                        },
                        {
                            "icon": "",
                            "id": "news",
                            "items": {"ExternalNews": 0, "News Item": 1},
                            "label": {"en": "News", "it": "Notizie"},
                        },
                        {
                            "icon": "",
                            "id": "announcements",
                            "items": {"Bando": 0},
                            "label": {"en": "Announcements", "it": "Bandi"},
                        },
                        {
                            "icon": "",
                            "id": "files-and-images",
                            "items": {"File": 0, "Image": 0},
                            "label": {
                                "en": "Files and images",
                                "it": "File e immagini",
                            },
                        },
                        {
                            "icon": "",
                            "id": "events",
                            "items": {"Event": 1},
                            "label": {"en": "Events", "it": "Eventi"},
                        },
                    ],
                    "label": {"en": "What"},
                    "type": "Groups",
                },
                {
                    "index": "Subject",
                    "items": {"aaa": 3, "bbb": 2},
                    "label": {"en": "Keywords", "it": "Parole chiave"},
                    "type": "KeywordIndex",
                },
            ],
        )

    def test_events_have_advanced_filters(self):
        query = {"SearchableText": "foo"}
        response = self.api_session.get(self.url, params=query)
        data = response.json()
        events_facets = data["facets"][0]["items"][-1]
        self.assertEqual(
            events_facets,
            {
                "icon": "",
                "id": "events",
                "items": {"Event": 1},
                "label": {"en": "Events", "it": "Eventi"},
            },
        )

    def test_filter_by_group_name_all_return_all_data(self):
        query = {"SearchableText": "foo"}
        response = self.api_session.get(self.url, params=query)

        query["group"] = "all"
        all_response = self.api_session.get(self.url, params=query)

        data = response.json()
        all_data = all_response.json()

        self.assertEqual(data["facets"], all_data["facets"])
        self.assertEqual(data["items_total"], all_data["items_total"])
        self.assertEqual(data["items"], all_data["items"])
        self.assertEqual(data["items_total"], 4)
        self.assertEqual(
            all_data["facets"],
            [
                {
                    "index": "portal_type",
                    "items": [
                        {
                            "id": "all",
                            "index": "portal_type",
                            "items": {
                                "Document": 1,
                                "Event": 1,
                                "Folder": 1,
                                "News Item": 1,
                            },
                            "label": {"en": "All content types"},
                        },
                        {
                            "icon": "",
                            "id": "documents",
                            "items": {"Document": 1},
                            "label": {"en": "Documents", "it": "Pagine"},
                        },
                        {
                            "icon": "",
                            "id": "news",
                            "items": {"ExternalNews": 0, "News Item": 1},
                            "label": {"en": "News", "it": "Notizie"},
                        },
                        {
                            "icon": "",
                            "id": "announcements",
                            "items": {"Bando": 0},
                            "label": {"en": "Announcements", "it": "Bandi"},
                        },
                        {
                            "icon": "",
                            "id": "files-and-images",
                            "items": {"File": 0, "Image": 0},
                            "label": {
                                "en": "Files and images",
                                "it": "File e immagini",
                            },
                        },
                        {
                            "icon": "",
                            "id": "events",
                            "items": {"Event": 1},
                            "label": {"en": "Events", "it": "Eventi"},
                        },
                    ],
                    "label": {"en": "What"},
                    "type": "Groups",
                },
                {
                    "index": "Subject",
                    "items": {"aaa": 3, "bbb": 2},
                    "label": {"en": "Keywords", "it": "Parole chiave"},
                    "type": "KeywordIndex",
                },
            ],
        )

    def test_filter_by_group_name_return_filtered_data(self):
        query = {"SearchableText": "foo", "group": "news"}
        response = self.api_session.get(self.url, params=query)
        data = response.json()

        self.assertEqual(data["items_total"], 1)
        self.assertEqual(data["items"][0]["@type"], "News Item")

        self.assertEqual(
            data["facets"],
            [
                {
                    "index": "portal_type",
                    "items": [
                        {
                            "id": "all",
                            "index": "portal_type",
                            "items": {
                                "Document": 1,
                                "Event": 1,
                                "Folder": 1,
                                "News Item": 1,
                            },
                            "label": {"en": "All content types"},
                        },
                        {
                            "icon": "",
                            "id": "documents",
                            "items": {"Document": 1},
                            "label": {"en": "Documents", "it": "Pagine"},
                        },
                        {
                            "icon": "",
                            "id": "news",
                            "items": {"ExternalNews": 0, "News Item": 1},
                            "label": {"en": "News", "it": "Notizie"},
                        },
                        {
                            "icon": "",
                            "id": "announcements",
                            "items": {"Bando": 0},
                            "label": {"en": "Announcements", "it": "Bandi"},
                        },
                        {
                            "icon": "",
                            "id": "files-and-images",
                            "items": {"File": 0, "Image": 0},
                            "label": {
                                "en": "Files and images",
                                "it": "File e immagini",
                            },
                        },
                        {
                            "icon": "",
                            "id": "events",
                            "items": {"Event": 1},
                            "label": {"en": "Events", "it": "Eventi"},
                        },
                    ],
                    "label": {"en": "What"},
                    "type": "Groups",
                },
                {
                    "index": "Subject",
                    "items": {"aaa": 1, "bbb": 1},
                    "label": {"en": "Keywords", "it": "Parole chiave"},
                    "type": "KeywordIndex",
                },
            ],
        )

    def test_filter_by_group_name_do_not_change_types_facet_but_update_other_indexes(
        self,
    ):
        query = {"SearchableText": "foo", "group": "news"}
        response = self.api_session.get(self.url, params=query)
        data = response.json()

        self.assertEqual(
            data["facets"],
            [
                {
                    "index": "portal_type",
                    "items": [
                        {
                            "id": "all",
                            "index": "portal_type",
                            "items": {
                                "Document": 1,
                                "Event": 1,
                                "Folder": 1,
                                "News Item": 1,
                            },
                            "label": {"en": "All content types"},
                        },
                        {
                            "icon": "",
                            "id": "documents",
                            "items": {"Document": 1},
                            "label": {"en": "Documents", "it": "Pagine"},
                        },
                        {
                            "icon": "",
                            "id": "news",
                            "items": {"ExternalNews": 0, "News Item": 1},
                            "label": {"en": "News", "it": "Notizie"},
                        },
                        {
                            "icon": "",
                            "id": "announcements",
                            "items": {"Bando": 0},
                            "label": {"en": "Announcements", "it": "Bandi"},
                        },
                        {
                            "icon": "",
                            "id": "files-and-images",
                            "items": {"File": 0, "Image": 0},
                            "label": {
                                "en": "Files and images",
                                "it": "File e immagini",
                            },
                        },
                        {
                            "icon": "",
                            "id": "events",
                            "items": {"Event": 1},
                            "label": {"en": "Events", "it": "Eventi"},
                        },
                    ],
                    "label": {"en": "What"},
                    "type": "Groups",
                },
                {
                    "index": "Subject",
                    "items": {"aaa": 1, "bbb": 1},  # this is updated
                    "label": {"en": "Keywords", "it": "Parole chiave"},
                    "type": "KeywordIndex",
                },
            ],
        )

    def test_filter_by_subject_return_filtered_results(self):
        query = {"SearchableText": "foo", "Subject": "bbb"}
        response = self.api_session.get(self.url, params=query)
        data = response.json()

        self.assertEqual(data["items_total"], 2)
        self.assertEqual(data["items"][0]["@type"], "Event")
        self.assertEqual(data["items"][1]["@type"], "News Item")

    def test_filter_by_subject_return_updated_facets_both_types_and_other_indexes(self):
        query = {"SearchableText": "foo", "Subject": "bbb"}
        response = self.api_session.get(self.url, params=query)
        data = response.json()

        self.assertEqual(
            data["facets"],
            [
                {
                    "index": "portal_type",
                    "items": [
                        {
                            "id": "all",
                            "index": "portal_type",
                            "items": {"Event": 1, "News Item": 1},
                            "label": {"en": "All content types"},
                        },
                        {
                            "icon": "",
                            "id": "documents",
                            "items": {"Document": 0},
                            "label": {"en": "Documents", "it": "Pagine"},
                        },
                        {
                            "icon": "",
                            "id": "news",
                            "items": {"ExternalNews": 0, "News Item": 1},
                            "label": {"en": "News", "it": "Notizie"},
                        },
                        {
                            "icon": "",
                            "id": "announcements",
                            "items": {"Bando": 0},
                            "label": {"en": "Announcements", "it": "Bandi"},
                        },
                        {
                            "icon": "",
                            "id": "files-and-images",
                            "items": {"File": 0, "Image": 0},
                            "label": {
                                "en": "Files and images",
                                "it": "File e immagini",
                            },
                        },
                        {
                            "icon": "",
                            "id": "events",
                            "items": {"Event": 1},
                            "label": {"en": "Events", "it": "Eventi"},
                        },
                    ],
                    "label": {"en": "What"},
                    "type": "Groups",
                },
                {
                    "index": "Subject",
                    "items": {"aaa": 1, "bbb": 2},
                    "label": {"en": "Keywords", "it": "Parole chiave"},
                    "type": "KeywordIndex",
                },
            ],
        )

    def test_filter_by_group_with_advanced_filters_add_new_facets(self):
        query = {"SearchableText": "foo", "group": "news"}
        response = self.api_session.get(self.url, params=query)
        data = response.json()

        self.assertEqual(len(data["facets"]), 2)

        query["group"] = "events"
        response = self.api_session.get(self.url, params=query)
        data = response.json()
        self.assertEqual(len(data["facets"]), 4)

        self.assertEqual(
            data["facets"],
            [
                {
                    "index": "portal_type",
                    "items": [
                        {
                            "id": "all",
                            "index": "portal_type",
                            "items": {
                                "Document": 1,
                                "Event": 1,
                                "Folder": 1,
                                "News Item": 1,
                            },
                            "label": {"en": "All content types"},
                        },
                        {
                            "icon": "",
                            "id": "documents",
                            "items": {"Document": 1},
                            "label": {"en": "Documents", "it": "Pagine"},
                        },
                        {
                            "icon": "",
                            "id": "news",
                            "items": {"ExternalNews": 0, "News Item": 1},
                            "label": {"en": "News", "it": "Notizie"},
                        },
                        {
                            "icon": "",
                            "id": "announcements",
                            "items": {"Bando": 0},
                            "label": {"en": "Announcements", "it": "Bandi"},
                        },
                        {
                            "icon": "",
                            "id": "files-and-images",
                            "items": {"File": 0, "Image": 0},
                            "label": {
                                "en": "Files and images",
                                "it": "File e immagini",
                            },
                        },
                        {
                            "icon": "",
                            "id": "events",
                            "items": {"Event": 1},
                            "label": {"en": "Events", "it": "Eventi"},
                        },
                    ],
                    "label": {"en": "What"},
                    "type": "Groups",
                },
                {
                    "index": "Subject",
                    "items": {"bbb": 1},
                    "label": {"en": "Keywords", "it": "Parole chiave"},
                    "type": "KeywordIndex",
                },
                {
                    "index": "start",
                    "items": {},
                    "label": {"en": "Start date"},
                    "type": "DateIndex",
                },
                {
                    "index": "end",
                    "items": {},
                    "label": {"en": "Start date"},
                    "type": "DateIndex",
                },
            ],
        )
