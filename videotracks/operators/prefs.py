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
from bpy.types import Operator, Menu

#############
# Preferences
#############


class UAS_MT_VideoTracks_Prefs_MainMenu(Menu):
    bl_idname = "UAS_MT_Video_Tracks_prefs_mainmenu"
    bl_label = "General Preferences"
    # bl_description = "General Preferences"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("preferences.addon_show", text="Add-on Preferences...").module = "videotracks"

        # row = layout.row(align=True)
        # row.operator("uas_video_tracks.general_prefs", text="Preferences...")

        # row = layout.row(align=True)
        # row.operator("uas_video_tracks.project_settings_prefs", text="Project Settings...")

        row = layout.row(align=True)
        row.operator(
            "videotracks.open_documentation_url", text="Documentation"
        ).path = "https://github.com/ubisoft/videotracks"

        layout.separator()

        row = layout.row(align=True)
        row.operator("uas_video_tracks.about", text="About...")


class UAS_VideoTracks_General_Prefs(Operator):
    bl_idname = "uas_video_tracks.general_prefs"
    bl_label = "General Preferences"
    bl_description = "Display the General Preferences panel"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        props = context.scene.UAS_video_tracks_props
        prefs = context.preferences.addons["videotracks"].preferences

        layout = self.layout

        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        box = layout.box()
        col = box.column()
        col.use_property_split = True
        # col.use_property_decorate = False

        col.prop(prefs, "new_shot_duration", text="Default Shot Length")

        layout.separator()
        if props.use_project_settings:
            row = layout.row()
            row.alert = True
            row.label(text="Overriden by Project Settings:")
        else:
            # layout.label(text="Others")
            pass
        box = layout.box()
        box.enabled = not props.use_project_settings
        col = box.column()
        col.use_property_split = True
        col.prop(props, "new_shot_prefix", text="Default Shot Prefix")

        # row = layout.row()
        # row.label(text="Handles:")
        col.prop(props, "render_shot_prefix")
        col.prop(props, "handles", text="Handles Duration")

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


_classes = (
    UAS_MT_VideoTracks_Prefs_MainMenu,
    UAS_VideoTracks_General_Prefs,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
