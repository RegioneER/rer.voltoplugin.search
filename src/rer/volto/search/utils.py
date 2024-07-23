from collective.volto.sitesettings.interfaces import (
    ICollectiveVoltoSitesettingsAdditionalSiteSchema,
)


try:
    from plone.base.interfaces.controlpanel import ISiteSchema
except ImportError:
    # Plone 52
    from Products.CMFPlone.interfaces import ISiteSchema


FIELD_MAPPING = {
    "site_logo": ISiteSchema,
    "site_logo_footer": ICollectiveVoltoSitesettingsAdditionalSiteSchema,
    "site_favicon": ISiteSchema,
}
