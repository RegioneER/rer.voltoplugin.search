from plone.restapi.controlpanels import RegistryConfigletPanel
from rer.voltoplugin.search.interfaces import IRERVoltopluginSearchControlpanel
from rer.voltoplugin.search.interfaces import IRERVoltopluginSearchLayer
from rer.voltoplugin.search.interfaces import IRERVoltopluginSearchSettings
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@adapter(Interface, IRERVoltopluginSearchLayer)
@implementer(IRERVoltopluginSearchControlpanel)
class RERVoltopluginSearchSettingsControlpanel(RegistryConfigletPanel):
    schema = IRERVoltopluginSearchSettings
    configlet_id = "RERVoltopluginSearchSettings"
    configlet_category_id = "Products"
    schema_prefix = None
