from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ISearchSchema
from zope.component import getUtility


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "rer.voltoplugin.search:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return ["rer.voltoplugin.search.upgrades"]


def post_install(context):
    """Post install script"""
    # Re-enable some types from search
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ISearchSchema, prefix="plone")
    enable_types = [
        "Link",
        "File",
    ]
    types = [x for x in settings.types_not_searched if x not in enable_types]
    settings.types_not_searched = tuple(types)


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
