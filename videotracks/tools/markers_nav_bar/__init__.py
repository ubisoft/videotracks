from . import markers_nav_bar_addon_prefs
from . import markers_nav_bar
from . import operators
from . import icons


def register():
    print("       - Registering Markers Nav Bar Package")

    icons.register()
    markers_nav_bar_addon_prefs.register()
    operators.register()
    markers_nav_bar.register()


def unregister():

    markers_nav_bar.unregister()
    operators.unregister()
    markers_nav_bar_addon_prefs.unregister()
    icons.register()
