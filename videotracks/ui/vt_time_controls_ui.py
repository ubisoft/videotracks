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
Time control panel
"""

import bpy

from bpy.types import Panel

import videotracks.config as config
from videotracks import display_version

from videotracks.tools.markers_nav_bar.markers_nav_bar import draw_markers_nav_bar

######
# Time control panel #
######


# class UAS_PT_VideoTracksTimeControlsInTimeline(Panel):
#     bl_idname = "UAS_PT_VideoTracksTimeControlsPanelInTimeline"
#     bl_label = "Time Control"
#     bl_description = "Time Control Options"
#     bl_space_type = "TIMELINE_EDITOR"
#     bl_region_type = "UI"
#     bl_category = "Time Controls"
#     #  bl_parent_id = "UAS_PT_Video_Tracks"
#     # bl_options = {"DEFAULT_CLOSED"}

#     @classmethod
#     def poll(cls, context):
#         prefs = context.preferences.addons["videotracks"].preferences
#         return prefs.tcmnavbars_display_in_timeline

#     def draw(self, context):
#         scene = context.scene


class UAS_PT_VideoTracksTimeControlsInVSE(Panel):
    bl_idname = "UAS_PT_VideoTracksTimeControlsPanelInVSE"
    bl_label = "UAS Time Controls   V. " + display_version
    bl_description = "Time Control Options"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Time Controls"
    #  bl_parent_id = "UAS_PT_Video_Tracks"
    # bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        prefs = context.preferences.addons["videotracks"].preferences
        return prefs.tcmnavbars_display_in_vse

    def draw_header(self, context):
        props = context.scene.UAS_video_tracks_props
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)

        # if context.window_manager.UAS_video_shot_manager_displayAbout:
        #     row.alert = True
        # else:
        #     row.alert = False

        icon = config.vt_icons_col["General_Ubisoft_32"]
        row.operator("uas_video_tracks.about", text="", icon_value=icon.icon_id)

    def draw_header_preset(self, context):
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)

        # row.operator("utils.launchrender", text="", icon="RENDER_STILL").renderMode = "STILL"
        # row.operator("utils.launchrender", text="", icon="RENDER_ANIMATION").renderMode = "ANIMATION"

        #    row.operator("render.opengl", text="", icon='IMAGE_DATA')
        #   row.operator("render.opengl", text="", icon='RENDER_ANIMATION').animation = True
        #    row.operator("screen.screen_full_area", text ="", icon = 'FULLSCREEN_ENTER').use_hide_panels=False

        # row.separator(factor=2)
        icon = config.vt_icons_col["General_Explorer_32"]
        row.operator("uas_video_tracks.open_explorer", text="", icon_value=icon.icon_id).path = bpy.path.abspath(
            bpy.data.filepath
        )

        row.separator(factor=1)
        row.menu("UAS_MT_Video_Tracks_prefs_mainmenu", icon="PREFERENCES", text="")

    def draw(self, context):
        scene = context.scene
        vt_props = scene.UAS_video_tracks_props
        layout = self.layout

        #########################################
        # Markers
        #########################################

        layout.label(text="Markers:")
        box = layout.box()
        row = box.row()
        draw_markers_nav_bar(context, row)

        #########################################
        # Zoom
        #########################################

        # layout.separator(factor=1)
        layout.label(text="VSE Zoom:")

        box = layout.box()
        row = box.row()
        row.operator("uas_video_tracks.zoom_view", text="Current Frame").zoomMode = "TOCURRENTFRAME"
        row.operator("uas_video_tracks.zoom_view", text="Time Range").zoomMode = "TIMERANGE"
        row.operator("uas_video_tracks.zoom_view", text="Sel. Clips").zoomMode = "SELECTEDCLIPS"
        row.operator("uas_video_tracks.zoom_view", text="All Clips").zoomMode = "ALLCLIPS"
        # op = row.operator("uas_video_tracks.zoom_view", text="Track Clips").zoomMode = "TRACKCLIPS"
        op = row.operator("uas_video_tracks.zoom_view", text="Track Clips")
        op.zoomMode = "TRACKCLIPS"
        op.trackIndex = vt_props.selected_track_index

        #########################################
        # Time
        #########################################

        # layout.separator(factor=1)
        layout.label(text="Time Range:")

        box = layout.box()
        row = box.row()
        row.operator("uas_video_tracks.frame_time_range", text="Frame Selected Clips").frameMode = "SELECTEDCLIPS"
        row.operator("uas_video_tracks.frame_time_range", text="Frame All Clips").frameMode = "ALLCLIPS"

        row = box.row(align=False)
        subRow = row.row(align=False)
        subRow.prop(scene, "use_preview_range", text="")
        subRow = row.row(align=True)
        if scene.use_preview_range:
            # row.use_property_split = False
            subRow.operator("uas_utils.get_current_frame_for_time_range", text="", icon="TRIA_UP_BAR").opArgs = (
                "{'frame_preview_start': " + str(scene.frame_current) + "}"
            )
            subRow.prop(scene, "frame_preview_start", text="Start")
            # subRow.operator("uas_video_tracks.frame_time_range", text="", icon="CENTER_ONLY")
            subRow.operator("uas_video_tracks.zoom_view", text="", icon="CENTER_ONLY").zoomMode = "TIMERANGE"
            subRow.prop(scene, "frame_preview_end", text="End")
            subRow.operator("uas_utils.get_current_frame_for_time_range", text="", icon="TRIA_UP_BAR").opArgs = (
                "{'frame_preview_end': " + str(scene.frame_current) + "}"
            )
            row.label(text=f"Duration: {scene.frame_preview_end - scene.frame_preview_start + 1}")
        else:
            subRow.operator("uas_utils.get_current_frame_for_time_range", text="", icon="TRIA_UP_BAR").opArgs = (
                "{'frame_start': " + str(scene.frame_current) + "}"
            )
            subRow.prop(scene, "frame_start", text="Start")
            # subRow.operator("uas_video_tracks.frame_time_range", text="", icon="CENTER_ONLY")
            subRow.operator("uas_video_tracks.zoom_view", text="", icon="CENTER_ONLY").zoomMode = "TIMERANGE"
            subRow.prop(scene, "frame_end", text="End")
            subRow.operator("uas_utils.get_current_frame_for_time_range", text="", icon="TRIA_UP_BAR").opArgs = (
                "{'frame_end': " + str(scene.frame_current) + "}"
            )
            row.label(text=f"Duration: {scene.frame_end - scene.frame_start + 1}")


_classes = (
    #  UAS_PT_VideoTracksTimeControlsInTimeline,
    UAS_PT_VideoTracksTimeControlsInVSE,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
