from plone.app.registry.browser import controlpanel
from rer.voltoplugin.search import _
from rer.voltoplugin.search.interfaces import IRERVoltopluginSearchSettings


class RERVoltopluginSearchForm(controlpanel.RegistryEditForm):
    schema = IRERVoltopluginSearchSettings
    label = _(
        "rer_volto_search_settings_controlpanel_label", default="RER Search Settings"
    )


class RERVoltopluginSearchControlPanel(controlpanel.ControlPanelFormWrapper):
    form = RERVoltopluginSearchForm
