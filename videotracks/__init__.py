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
Add-on initialization
"""


import os
from pathlib import Path

import bpy

from bpy.app.handlers import persistent

from bpy.props import IntProperty
from bpy.props import BoolProperty


from .config import config
from videotracks.config import sm_logging

_logger = sm_logging.getLogger(__name__)


bl_info = {
    "name": "Video Tracks",
    "author": "Ubisoft - Julien Blervaque (aka Werwack)",
    "description": "Introduce tracks to the Blender VSE - Ubisoft",
    "blender": (3, 0, 0),
    "version": (0, 2, 1),
    "location": "View3D > Video Tracks",
    "wiki_url": "https://github.com/ubisoft/videotracks",
    "warning": "BETA Version",
    "category": "Ubisoft",
}

__version__ = ".".join(str(i) for i in bl_info["version"])
display_version = __version__


def register():

    from .utils import utils

    versionTupple = utils.display_addon_registered_version("Video Tracks")

    config.initGlobalVariables()

    sm_logging.initialize()
    if config.devDebug:
        _logger.setLevel("DEBUG")  # CRITICAL ERROR WARNING INFO DEBUG NOTSET

    logger_level = f"Logger level: {sm_logging.getLevelName()}"
    versionTupple = utils.display_addon_registered_version("Video Tracks", more_info=logger_level)

    # install dependencies and required Python libraries
    ###################
    # try to install dependencies and collect the errors in case of troubles
    # If some mandatory libraries cannot be loaded then an alternative Add-on Preferences panel
    # is used and provide some visibility to the user to solve the issue
    # Pillow lib is installed there
    from .install.install_dependencies import install_dependencies

    installErrorCode = install_dependencies([("opentimelineio", "opentimelineio")], retries=1, timeout=5)
    if 0 != installErrorCode:
        print("  *** OpenTimelineIO install failed for UbisoftVideo Tracks ***")
        return installErrorCode
    print("  OpenTimelineIO correctly installed for Ubisoft Video Tracks")

    # if install went right then register other packages
    ###################
    from .operators import prefs
    from .operators import general
    from .operators import tracks

    from . import otio
    from .properties import vt_props

    # from .ui.vsm_ui import UAS_PT_VideoTracks
    from .ui import vt_ui
    from .ui import vt_panels_ui
    from .ui import vt_time_controls_ui

    from .operators import about
    from .operators import vt_tools

    from .properties import addon_prefs

    from .tools import vse_render
    from .tools import markers_nav_bar
    from .tools import time_controls_bar

    from .utils import utils_operators

    from .opengl import sequencer_draw

    ###################
    # update data
    ###################

    bpy.types.WindowManager.UAS_video_tracks_version = IntProperty(
        name="Add-on Version Int", description="Add-on version as integer", default=versionTupple[1]
    )

    def on_toggle_overlay_updated(self, context):
        if self.UAS_video_tracks_overlay:
            print("on_toggle_overlay_updated")
            bpy.ops.uas_video_tracks.tracks_overlay("INVOKE_DEFAULT")

    bpy.types.WindowManager.UAS_video_tracks_overlay = BoolProperty(
        name="Toggle Overlay", default=False, update=on_toggle_overlay_updated
    )

    # utils_handlers.removeAllHandlerOccurences(
    #     checkDataVersion_post_load_handler, handlerCateg=bpy.app.handlers.load_post
    # )
    # bpy.app.handlers.load_post.append(checkDataVersion_post_load_handler)

    # if config.devDebug:
    #     utils_handlers.displayHandlers(handlerCategName="load_post")

    # initialization
    ##################

    # data version is written in the initialize function
    # bpy.types.WindowManager.UAS_shot_manager_isInitialized = BoolProperty(
    #     name="Shot Manager is initialized", description="", default=False
    # )

    # utils_handlers.displayHandlers()
    #   utils_handlers.removeAllHandlerOccurences(jump_to_shot, handlerCateg=bpy.app.handlers.frame_change_pre)
    # utils_handlers.removeAllHandlerOccurences(
    #     jump_to_shot__frame_change_post, handlerCateg=bpy.app.handlers.frame_change_post
    # )
    # utils_handlers.displayHandlers()

    # for cls in classes:
    #     bpy.utils.register_class(cls)

    otio.register()

    addon_prefs.register()

    markers_nav_bar.register()
    time_controls_bar.register()

    utils_operators.register()
    #   utils_vse.register()

    # operators
    prefs.register()
    # markers_nav_bar_addon_prefs.register()

    vse_render.register()

    general.register()

    vt_props.register()
    tracks.register()
    vt_tools.register()

    # ui
    vt_ui.register()
    vt_panels_ui.register()
    vt_time_controls_ui.register()

    sequencer_draw.register()

    about.register()

    if config.devDebug:
        print(f"\n ------ Video Tracks debug: {config.devDebug} ------- ")


def unregister():

    from .operators import prefs
    from .operators import general
    from .operators import tracks

    from . import otio
    from .properties import vt_props

    # from .ui.vsm_ui import UAS_PT_VideoTracks
    from .ui import vt_ui
    from .ui import vt_panels_ui
    from .ui import vt_time_controls_ui

    from .operators import about
    from .operators import vt_tools

    from .properties import addon_prefs

    from .tools import vse_render
    from .tools import markers_nav_bar
    from .tools import time_controls_bar

    from .utils import utils_operators

    from .opengl import sequencer_draw

    print("\n*** --- Unregistering UAS Video Tracks Add-on --- ***\n")

    # utils_handlers.removeAllHandlerOccurences(
    #     checkDataVersion_post_load_handler, handlerCateg=bpy.app.handlers.load_post
    # )

    # debug tools
    # if config.devDebug:
    #     sm_debug.unregister()

    try:
        sequencer_draw.unregister()
    except Exception:
        print("Error (handled) in Unregister sequencer_draw")
    vt_time_controls_ui.unregister()
    vt_panels_ui.unregister()
    vt_ui.unregister()
    vt_tools.unregister()
    tracks.unregister()
    vt_props.unregister()
    prefs.unregister()
    general.unregister()

    vse_render.unregister()

    # ui
    about.unregister()

    utils_operators.unregister()
    time_controls_bar.unregister()
    markers_nav_bar.unregister()
    # markers_nav_bar_addon_prefs.unregister()

    addon_prefs.unregister()

    otio.unregister()
    #  utils_vse.unregister()

    # for cls in reversed(classes):
    #     bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.UAS_video_tracks_version

    config.releaseGlobalVariables()

