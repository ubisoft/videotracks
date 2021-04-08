from . import time_controls_bar
from . import operators

# from . import icons


def register():
    print("       - Registering Time Controls Bar Package")

    #    icons.register()
    time_controls_bar.register()
    operators.register()


def unregister():

    operators.unregister()
    time_controls_bar.unregister()


#    icons.unregister()
