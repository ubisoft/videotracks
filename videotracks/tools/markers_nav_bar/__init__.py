from . import markers_nav_bar_addon_prefs
from . import markers_nav_bar
from . import operators


def register():
    print("       - Registering Markers Nav Bar Package")

    markers_nav_bar_addon_prefs.register()
    operators.register()
    markers_nav_bar.register()


def unregister():

    markers_nav_bar.unregister()
    operators.unregister()
    markers_nav_bar_addon_prefs.unregister()

