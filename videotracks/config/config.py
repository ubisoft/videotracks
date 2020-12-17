import bpy

import os
from pathlib import Path
import bpy.utils.previews


def initGlobalVariables():

    # debug ############
    global uasDebug

    # wkip better code: uasDebug = os.environ.get("UasDebug", "0") == "1"
    if "UasDebug" in os.environ.keys():
        uasDebug = bool(int(os.environ["UasDebug"]))
    else:
        uasDebug = True

    uasDebug = True

    # icons ############
    global vt_icons_col

    pcoll = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), "../icons")
    for png in Path(my_icons_dir).rglob("*.png"):
        pcoll.load(png.stem, str(png), "IMAGE")

    vt_icons_col = pcoll


def releaseGlobalVariables():

    global vt_icons_col

    bpy.utils.previews.remove(vt_icons_col)
    vt_icons_col = None
