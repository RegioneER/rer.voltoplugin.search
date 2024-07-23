from plone.app.registry.browser import controlpanel
from rer.volto.search import _
from rer.volto.search.interfaces import IRERVoltoSearchSettings


class RERVoltoSearchForm(controlpanel.RegistryEditForm):
    schema = IRERVoltoSearchSettings
    label = _(
        "rer_volto_search_settings_controlpanel_label", default="RER Search Settings"
    )


class RERVoltoSearchControlPanel(controlpanel.ControlPanelFormWrapper):
    form = RERVoltoSearchForm
