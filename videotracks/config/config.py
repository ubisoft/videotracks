# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
To do: module description here.
"""

import bpy

import os
from pathlib import Path
import bpy.utils.previews


def initGlobalVariables():

    # debug ############
    global devDebug

    # wkip better code: devDebug = os.environ.get("UasDebug", "0") == "1"
    if "devDebug" in os.environ.keys():
        devDebug = bool(int(os.environ["devDebug"]))
    else:
        devDebug = True

    devDebug = False

    global devDebug_ignoreLoggerFormatting
    devDebug_ignoreLoggerFormatting = True and devDebug

    # icons ############
    global vt_icons_col

    pcoll = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), "../icons")
    for png in Path(my_icons_dir).rglob("*.png"):
        pcoll.load(png.stem, str(png), "IMAGE")

    vt_icons_col = pcoll


def releaseGlobalVariables():

    global vt_icons_col

    try:
        bpy.utils.previews.remove(vt_icons_col)
    except Exception:
        pass

    vt_icons_col = None
