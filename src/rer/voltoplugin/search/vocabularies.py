from plone import api
from plone.api.exc import InvalidParameterError
from rer.voltoplugin.search.interfaces import IRERVoltopluginSearchCustomFilters
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


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
        pc = api.portal.get_tool(name="portal_catalog")
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
            if x.provided == IRERVoltopluginSearchCustomFilters
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
        factory = getUtility(IVocabularyFactory, voc_id)
        data = factory(context)
        if HAS_SOLR:
            try:
                if api.portal.get_registry_record(
                    "active", interface=IRerSolrpushSettings
                ):
                    voc_id = "rer.solrpush.vocabularies.AvailablePortalTypes"
                factory = getUtility(IVocabularyFactory, voc_id)
                solr_data = factory(context)
                if solr_data:
                    data = solr_data
            except (KeyError, InvalidParameterError):
                pass
        return data


AdvancedFiltersVocabularyFactory = AdvancedFiltersVocabulary()
GroupingTypesVocabularyFactory = GroupingTypesVocabulary()
IndexesVocabularyFactory = IndexesVocabulary()
