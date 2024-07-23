from plone.restapi.controlpanels import RegistryConfigletPanel
from .interfaces import IRERVoltoSearchControlpanel
from .interfaces import IRERVoltoSearchLayer
from .interfaces import IRERVoltoSearchSettings
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@adapter(Interface, IRERVoltoSearchLayer)
@implementer(IRERVoltoSearchControlpanel)
class RERVoltoSearchSettingsControlpanel(RegistryConfigletPanel):
    schema = IRERVoltoSearchSettings
    configlet_id = "RERVoltoSearchSettings"
    configlet_category_id = "Products"
    schema_prefix = None
