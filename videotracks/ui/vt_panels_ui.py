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

from bpy.types import Panel, Operator
from bpy.props import StringProperty


class UAS_VideoTracks_SelectStrip(Operator):
    bl_idname = "uas_videovideotracks.select_strip"
    bl_label = "Select"
    bl_description = "Select Strip"
    bl_options = {"INTERNAL"}

    # @classmethod
    # def poll(cls, context):
    #     props = context.scene.UAS_video_tracks_props
    #     val = len(props.getTakes()) and len(props.get_shots())
    #     return val

    # def invoke(self, context, event):
    #     props = context.scene.UAS_video_tracks_props

    #     return {"FINISHED"}
    # can be "SEL_SEQ", "ACTIVE"
    mode: StringProperty("SEL_SEQ")

    def execute(self, context):
        scene = context.scene

        if "SEL_SEQ" == self.mode:
            if bpy.context.selected_sequences is not None and 1 == len(bpy.context.selected_sequences):
                seq = bpy.context.selected_sequences[0]
                seq.select = False
                seq.select = True
        elif "ACTIVE" == self.mode:
            if scene.sequence_editor.active_strip is not None:
                seq = scene.sequence_editor.active_strip
                seq.select = False
                seq.select = True

        return {"FINISHED"}


class UAS_PT_VideoTracksSelectedStrip(Panel):
    bl_idname = "UAS_PT_VideoTracksSelectedStripPanel"
    bl_label = "Active Strip"
    bl_description = "Active Strip Options"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "UAS Video Shot Man"
    bl_parent_id = "UAS_PT_Video_Tracks"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        scene = context.scene
        prefs = context.preferences.addons["videotracks"].preferences
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.separator(factor=1)
        row.label(text="Active Strip:")
        subRow = row.row()
        # if bpy.context.selected_sequences is not None and 1 == len(bpy.context.selected_sequences):
        #     subRow.prop(bpy.context.selected_sequences[0], "name", text="")
        if scene.sequence_editor is not None and scene.sequence_editor.active_strip is not None:
            subRow.prop(scene.sequence_editor.active_strip, "name", text="")
        else:
            subRow.enabled = False
            subRow.prop(prefs, "markerEmptyField", text="")
        subRow.operator(
            "uas_videovideotracks.select_strip", text="", icon="RESTRICT_SELECT_OFF"
        ).mode = "ACTIVE"  # "SEL_SEQ"

        row = box.row()
        row.separator(factor=1)
        row.label(text="Type:")
        if bpy.context.selected_sequences is not None and 1 == len(bpy.context.selected_sequences):
            row.label(text=str(type(bpy.context.selected_sequences[0]).__name__))

        # if config.devDebug:
        #     box = layout.box()
        #     box.label(text="Tools:")
        #     row = box.row()
        #     #  row.operator("uas_video_tracks.selected_to_active")

        #     box = layout.box()

        #     row = box.row()
        #     row.separator(factor=0.1)


_classes = (
    UAS_PT_VideoTracksSelectedStrip,
    UAS_VideoTracks_SelectStrip,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
