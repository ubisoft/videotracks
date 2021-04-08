"""
This module defines the list of the custom icons used by VRtist panel.
"""

import bpy

import os
from pathlib import Path
import bpy.utils.previews


def register():

    global icons_col

    pcoll = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), ".")
    for png in Path(my_icons_dir).rglob("*.png"):
        pcoll.load(png.stem, str(png), "IMAGE")

    icons_col = pcoll


def unregister():

    global icons_col
    print("Unregister Marker nav icons")

    try:
        bpy.utils.previews.remove(icons_col)
    except Exception:
        pass

    icons_col = None
