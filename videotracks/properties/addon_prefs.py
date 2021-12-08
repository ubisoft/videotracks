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
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, FloatProperty, FloatVectorProperty

from videotracks.tools.markers_nav_bar.markers_nav_bar_addon_prefs import draw_markers_nav_bar_settings

from videotracks.utils.utils_ui import collapsable_panel


class UAS_VideoTracks_AddonPrefs(AddonPreferences):
    """
        Use this to get these prefs:
        prefs = context.preferences.addons["videotracks"].preferences
    """

    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package
    # bl_idname = __package__
    bl_idname = "videotracks"

    ##################
    # general ###
    ##################

    tracks_list_panel_opened: BoolProperty(default=False,)

    ##################
    # ui helpers   ###
    ##################

    # used for example as a placehoder in VSM to have a text field when no strip is selected
    emptyField: StringProperty(name=" ")
    emptyBool: BoolProperty(name=" ", default=False)

    ##################
    # UI tracks values   ###
    ##################

    showTrackHeaders: BoolProperty(default=True)
    trackHeaderWidth: FloatProperty(default=5.0)
    trackHeadeOpacity: FloatProperty(default=0.9)

    trackHeaderColor: FloatVectorProperty(
        name="Track Color",
        description="Color of the track header",
        subtype="COLOR",
        size=3,
        min=0.0,
        max=1.0,
        precision=2,
        # get=_get_color,
        # set=_set_color,
        default=[0.9, 0.0, 0.0],
    )

    ##################
    # Markers Nav Bar Settings ###
    ##################

    mnavbar_pref_panel_opened: BoolProperty(default=False,)

    mnavbar_display_in_vse: BoolProperty(
        name="Display in VSE", description="Display Markers Nav Bar in the VSE toolbar", default=True,
    )
    mnavbar_display_in_timeline: BoolProperty(
        name="Display in Timeline", description="Display Markers Nav Bar in the Timeline toolbar", default=False,
    )
    mnavbar_display_filter: BoolProperty(
        name="Display Filter", description="Display the filter tools", default=True,
    )

    # Markers Nav Bar component controls ###

    markerEmptyField: StringProperty(name=" ")

    mnavbar_use_filter: BoolProperty(
        name="Filter Markers", default=False,
    )

    mnavbar_filter_text: StringProperty(
        name="Filter Text", default="",
    )

    def _update_mnavbar_use_view_frame(self, context):
        if self.mnavbar_use_view_frame:
            try:
                bpy.ops.sequencer.view_frame()
            except Exception as e:
                # context is timeline, not VSE
                pass
        print("\n*** mnavbar_use_view_frame. New state: ", self.mnavbar_use_view_frame)

    mnavbar_use_view_frame: BoolProperty(
        name="View Frame", default=True, update=_update_mnavbar_use_view_frame,
    )

    ##################
    # Time Controls Bar Settings ###
    ##################

    tcbar_pref_panel_opened: BoolProperty(default=False,)

    tcbar_display_in_vse: BoolProperty(
        name="Display in VSE", description="Display Time Controls Bar in the VSE toolbar", default=True,
    )
    tcbar_display_in_timeline: BoolProperty(
        name="Display in Timeline", description="Display Time Controls Bar in the Timeline toolbar", default=True,
    )

    ##################
    # Time Controls Bar and Markers panel ###
    ##################

    tcmnavbars_display_in_vse: BoolProperty(
        name="Display Panel in VSE",
        description="Display Time Controls and Markers Bars in the VSE tabs bar",
        default=True,
    )
    tcmnavbars_display_in_timeline: BoolProperty(
        name="Display Panel in Timeline",
        description="Display Time Controls and Markers Bars in the Timeline tabs bar",
        default=True,
    )

    ##################################################################################
    # Draw
    ##################################################################################
    def draw(self, context):
        scene = context.scene
        prefs = context.preferences.addons["videotracks"].preferences

        #        draw_preferences_ui(self, context)
        layout = self.layout

        layout.label(text="Tools:")
        box = layout.box()
        # prefs = context.preferences.addons["videotracks"].preferences
        # prefs.draw_markers_nav_bar_settings(self, context)

        collapsable_panel(box, prefs, "mnavbar_pref_panel_opened", text="Markers Nav Bar")
        if prefs.mnavbar_pref_panel_opened:
            draw_markers_nav_bar_settings(self, context, box)

        row = layout.row()
        row.separator()
        row.label(text="Time Controls and Markers Panel:")

        row = layout.row()
        row.separator()
        box = row.box()

        row = box.row(align=False)
        row.separator()
        row.prop(prefs, "tcmnavbars_display_in_vse")

        # row = box.row(align=False)
        # row.separator()
        # row.prop(prefs, "tcmnavbars_display_in_timeline")

        #     box = layout.box()
        #     box.use_property_decorate = False
        #     col = box.column()
        #     col.use_property_split = True
        #     col.prop(prefs, "new_shot_duration", text="Default Shot Length")
        #    col.prop(prefs, "useLockCameraView", text="Use Lock Camera View")

        layout.label(text="Track Headers")
        box = layout.box()

        box.prop(self, "showTrackHeaders")
        box.prop(self, "trackHeaderWidth")
        box.prop(self, "trackHeadeOpacity")
        box.prop(self, "trackHeaderColor")

    # layout.label(
    #     text="Temporary preference values (for dialogs for instance) are only visible when global variable devDebug is True."
    # )

    # if config.devDebug:
    #     layout.label(text="Add New Shot Dialog:")
    #     box = layout.box()
    #     col = box.column(align=False)
    #     col.prop(self, "addShot_start")
    #     col.prop(self, "addShot_end")


_classes = (UAS_VideoTracks_AddonPrefs,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

