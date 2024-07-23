from plone import api
from plone.api.exc import InvalidParameterError
from rer.volto.search.interfaces import IRERVoltoSearchCustomFilters
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.site.hooks import getSite


try:
    from rer.solrpush.interfaces.settings import IRerSolrpushSettings

    HAS_SOLR = True
except ImportError:
    HAS_SOLR = False


@implementer(IVocabularyFactory)
class IndexesVocabulary:
    """
    Vocabulary factory for allowable indexes in catalog.
    """

    def __call__(self, context):
        site = getSite()
        pc = api.portal.get_tool(site, "portal_catalog")
        indexes = list(pc.indexes())
        indexes.sort()
        indexes = [SimpleTerm(i, i, i) for i in indexes]
        return SimpleVocabulary(indexes)


@implementer(IVocabularyFactory)
class AdvancedFiltersVocabulary:
    """
    Vocabulary factory for list of advanced filters
    """

    def __call__(self, context):
        sm = getGlobalSiteManager()
        request = getRequest()
        adapters = [
            {
                "name": x.name,
                "label": translate(x.factory.label, context=request),
            }
            for x in sm.registeredAdapters()
            if x.provided == IRERVoltoSearchCustomFilters
        ]
        terms = [
            SimpleTerm(
                value=i["name"],
                token=i["name"],
                title=i["label"],
            )
            for i in sorted(adapters, key=lambda i: i["label"])
        ]
        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class GroupingTypesVocabulary:
    """ """

    def __call__(self, context):
        voc_id = "plone.app.vocabularies.ReallyUserFriendlyTypes"
        if HAS_SOLR:
            try:
                if api.portal.get_registry_record(
                    "active", interface=IRerSolrpushSettings
                ):
                    voc_id = "rer.solrpush.vocabularies.AvailablePortalTypes"
            except (KeyError, InvalidParameterError):
                pass
        factory = getUtility(IVocabularyFactory, voc_id)
        return factory(context)


AdvancedFiltersVocabularyFactory = AdvancedFiltersVocabulary()
GroupingTypesVocabularyFactory = GroupingTypesVocabulary()
IndexesVocabularyFactory = IndexesVocabulary()
