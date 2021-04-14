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

# -*- coding: utf-8 -*-
import bpy, bgl, blf, gpu
from gpu_extras.batch import batch_for_shader


# def get_rectangle_region_coordinates(rectangle=(0, 0, 5, 5), view_boundaries=(0, 0, 1920, 1080)):
#     """Calculates strip coordinates in region's pixels norm, clamped into region

#     :param rectangle: Rectangle to get coordinates of
#     :param view_boundaries: Cropping area
#     :return: Strip coordinates in region's pixels norm, resized for status color bar
#     """
#     region = bpy.context.region

#     # Converts x and y in terms of the grid's frames and channels to region pixels coordinates clamped
#     x1, y1 = region.view2d.view_to_region(
#         max(view_boundaries[0], min(rectangle[0], view_boundaries[2])),
#         max(view_boundaries[1], min(rectangle[1], view_boundaries[3])),
#     )
#     x2, y2 = region.view2d.view_to_region(
#         max(view_boundaries[0], min(rectangle[2], view_boundaries[2])),
#         max(view_boundaries[1], min(rectangle[3], view_boundaries[3])),
#     )

#     return x1, y1, x2, y2


# def build_rectangle(coordinates, indices=((0, 1, 2), (2, 1, 3))):
#     """Build an OpenGL rectangle into region

#     :param coordinates: Four points coordinates
#     :param indices: Rectangle's indices
#     :return: Built vertices and indices
#     """
#     # Building the Rectangle
#     vertices = (
#         (coordinates[0], coordinates[1]),
#         (coordinates[2], coordinates[1]),
#         (coordinates[0], coordinates[3]),
#         (coordinates[2], coordinates[3]),
#     )

#     return vertices, indices


# def draw_rect(rect_width, shader, i, view_boundaries):
#     region = bpy.context.region
#     x_view_fixed, y_view_fixed = region.view2d.region_to_view(20, 50)

#     # Build track rectangle
#     track_rectangle = get_rectangle_region_coordinates((x_view_fixed, i + 1, x_view_fixed, i + 2), view_boundaries)

#     vertices, indices = build_rectangle(
#         (track_rectangle[0], track_rectangle[1], track_rectangle[2] + rect_width, track_rectangle[3],)
#     )

#     # Draw the rectangle
#     batch = batch_for_shader(shader, "TRIS", {"pos": vertices}, indices=indices)
#     batch.draw(shader)


# def draw_channel_name(tracks, view_boundaries):
#     """Draw tracks name

#     :param view_boundaries: View boundaries
#     """
#     region = bpy.context.region
#     font_id = 0

#     x_view_fixed, y_view_fixed = region.view2d.region_to_view(20, 50)
#     width_track_frame_fixed = 150
#     shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")
#     shader.bind()

#     # Draw track rectangles
#     bgl.glEnable(bgl.GL_BLEND)  # Enables alpha channel
#     dark_track = False
#     for i, track in enumerate(reversed(tracks)):  # Out of text loop because of OpenGL issue, rectangles are bugging
#         # shader.uniform_float("color", (0.66, 0.66, 0.66, 0.7))
#         shader.uniform_float("color", (track.color[0], track.color[1], track.color[2], 0.7))

#         # Alternate track color
#         # if dark_track:
#         #     shader.uniform_float("color", (0.5, 0.5, 0.5, 0.7))
#         # dark_track = not dark_track

#         draw_rect(width_track_frame_fixed, shader, i, view_boundaries)

#         # draw selected rect
#         vt_props = bpy.context.scene.UAS_video_tracks_props
#         currentTrackInd = vt_props.getSelectedTrackIndex()
#         if i + 1 == currentTrackInd:
#             # shader.uniform_float("color", (0.5, 0.2, 0.2, 0.2))
#             shader.uniform_float("color", (track.color[0], track.color[1], track.color[2], 0.15))
#             draw_rect(1800, shader, i, view_boundaries)

#         # # Build track rectangle
#         # track_rectangle = get_rectangle_region_coordinates((x_view_fixed, i + 1, x_view_fixed, i + 2), view_boundaries)

#         # vertices, indices = build_rectangle(
#         #     (track_rectangle[0], track_rectangle[1], track_rectangle[2] + width_track_frame_fixed, track_rectangle[3],)
#         # )

#         # # Draw the rectangle
#         # batch = batch_for_shader(shader, "TRIS", {"pos": vertices}, indices=indices)
#         # batch.draw(shader)

#     # Display text
#     for i, track in enumerate(reversed(tracks)):
#         x, y = region.view2d.view_to_region(x_view_fixed, i + 1.4)

#         blf.position(font_id, 30, y, 0)
#         blf.size(font_id, 12, 72)
#         blf.color(font_id, 1, 1, 1, 0.9)
#         blf.draw(font_id, track.name)

#         i += 1


# def draw_sequencer():
#     """Draw sequencer OpenGL"""
#     # if True == True:
#     # return ()
#     # Sentinel if no sequences, abort
#     # if not hasattr(bpy.context.scene.sequence_editor, "sequences"):
#     #     return
#     props = bpy.context.scene.UAS_video_tracks_props
#     region = bpy.context.region

#     # Defining boundaries of the area to crop rectangles in view pixels' space
#     x_view_min, y_view_min = region.view2d.region_to_view(0, 11)
#     x_view_max, y_view_max = region.view2d.region_to_view(region.width - 11, region.height - 22)
#     view_boundaries = (x_view_min, y_view_min, x_view_max, y_view_max)

#     draw_channel_name(props.tracks, view_boundaries)


from .bgl_ui import BGL_UIOperatorBase, BGLCanvas
from .bgl_ui.widgets import *
from .bgl_ui.geometry import *
from .bgl_ui.types import BGLViewToRegion


class UAS_VideoTracks_TracksOverlay(BGL_UIOperatorBase):
    bl_idname = "uas_video_tracks.tracks_overlay"
    bl_label = "Draw tracks overlay."
    bl_options = {"REGISTER", "INTERNAL"}

    def __init__(self):
        BGL_UIOperatorBase.__init__(self)

    def build_ui(self):
        props = bpy.context.scene.UAS_video_tracks_props
        self.track_count = len(props.tracks)  # used for rebuilding ui

        # colors
        out_of_range_color = (BGLColor(0.1, 0.0, 0, 0.25)).to_sRGB()
        # bgColor = BGLColor(0.258, 0.258, 0.258)
        bgColorOri = BGLColor(0.258, 0.258, 0.258)
        bgColor = BGLColor(bgColorOri.r + 0.03, bgColorOri.g + 0.03, bgColorOri.b + 0.03)
        bgColor = BGLColor(0.258, 0.258, 0.258)
        bgColorAlt = BGLColor(bgColor.r * 0.9, bgColor.g * 0.9, bgColor.b * 0.9)
        textColor = BGLColor(0.9, 0.9, 0.9)
        selectedColor = BGLColor(0.99, 0.99, 0.99, 0.2)

        canva = BGLCanvas(BGLViewToRegion(), 0, 11, 11, 22)
        self.add_canva(canva)
        size = 100000

        # Out of time range colored areas
        #################################
        b = BGLRect(width=size, height=size * 2)
        b.color = out_of_range_color
        frame_range_left = BGLGeometryStamp(
            position=lambda: BGLCoord(-size + bpy.context.scene.frame_start, -size), geometry=b
        )

        b = BGLRect(width=size, height=size * 2)
        b.color = out_of_range_color
        frame_range_right = BGLGeometryStamp(position=lambda: BGLCoord(bpy.context.scene.frame_end, -size), geometry=b)
        canva.addWidget(frame_range_left)
        canva.addWidget(frame_range_right)

        canva = BGLCanvas(BGLViewToRegion(apply_to_x=False), 0, 11, 11, 22)
        self.add_canva(canva)

        # selected track highlight
        ##########################
        rect = BGLRect(width=9999999, height=1)
        track_selected_frame = BGLGeometryStamp(
            position=lambda prop=props: BGLCoord(0, prop.selected_track_index), geometry=rect
        )
        rect.color = lambda prop=props: selectedColor
        # rect.color = lambda prop=props: BGLColor(
        #     prop.tracks[prop.selected_track_index_inverted].color[0],
        #     prop.tracks[prop.selected_track_index_inverted].color[1],
        #     prop.tracks[prop.selected_track_index_inverted].color[2],
        #     0.2,
        # )
        canva.addWidget(track_selected_frame)

        img_man = BGLImageManager()
        # img = img_man.load_image(r"C:\\Users\rcarriquiryborchia\Pictures\Wip\casent0103346_d_1_high.jpg")

        display_slider = False
        header_width = 200
        channelDisplayWidth = 25

        for i, track in enumerate(reversed(props.tracks)):

            # header BG button
            ##################
            pos = BGLCoord(0, i + 1)

            def get_header_color ( my_index = i + 1):
                header_color = bgColor if 0 == my_index % 2 else bgColorAlt
                if my_index == props.selected_track_index:
                    header_color = BGLColor(header_color.r + 0.3, header_color.g + 0.3, header_color.b + 0.3)

                return header_color

            button = BGLButton(
                position=pos,
                width=header_width,
                height=1,
                text=lambda track=track: track.name,
                color=get_header_color,
                text_size=13,
                text_color=textColor,
                # color=lambda track=track: BGLColor(track.color[0], track.color[1], track.color[2]),
                # icon=img,
            )

            # button.text_size = lambda text_size=text_size: 18
            button.clicked_callback = lambda prop=props, index=i: prop.setSelectedTrackByIndex(index + 1)
            canva.addWidget(button)

            # channel label
            #################
            # pos = BGLCoord(0, i + 1)
            # label = BGLLabel(
            #     position=pos,
            #     width=channelDisplayWidth,
            #     height=1,
            #     text=str(i + 1) + ("  " if i < 9 else ""),
            #     rotation=1.57,
            #     text_size=15,
            # )
            pos = BGLCoord(0, i + 1)
            label = BGLLabel(position=pos, width=channelDisplayWidth, height=1, text=str(i + 1), text_size=13,)
            label.bgColor.a = 0.0
            label.text_alignment = "CENTER"
            canva.addWidget(label)

            # track opacity slider
            ######################
            slider_height = 0.2
            slider = BGLSlider(position=pos, width=header_width, height=slider_height)
            slider.value = lambda t=track: t.opacity
            slider.front_color = lambda t=track: BGLColor.blended(
                BGLColor(0.4, 0.4, 1), BGLColor(0.1, 0.1, 0.4), t.opacity / 100.0
            )

            def update_opacity(v, t=track):
                t.opacity = v

            slider.on_value_changed = update_opacity
            if display_slider:
                canva.addWidget(slider)

            # track enabled button
            ######################
            pos = BGLCoord(channelDisplayWidth + 26, pos.y + slider_height + 0.15)
            enabled_btn = BGLButton(
                position=pos,
                width=20,
                height=1 - slider_height - 2 * 0.15,
                text="V",
                color=lambda t=track: BGLColor(0.316, 0.465, 0.695) if t.enabled else BGLColor(0.398, 0.398, 0.398),
            )

            def update_enabled(t=track):
                t.enabled = not t.enabled

            enabled_btn.clicked_callback = update_enabled
            canva.addWidget(enabled_btn)

            # track color button
            ####################
            offset_from_side = 0.04
            pos = BGLCoord(channelDisplayWidth + 6, i + 1 + offset_from_side)
            # offset_from_side = 0.04
            # pos = BGLCoord(header_width - 14, i + 1 + offset_from_side)
            button = BGLButton(
                position=pos,
                width=12,
                height=1 - offset_from_side * 2,
                color=lambda track=track: (BGLColor(track.color[0], track.color[1], track.color[2])).to_linear(),
                text="",
                text_size=13,
                text_color=textColor,
                # icon=img,
            )

            # button.text_size = lambda text_size=text_size: 18
            button.clicked_callback = lambda prop=props, index=i: prop.setSelectedTrackByIndex(index + 1)
            canva.addWidget(button)

        ###############
        # Debug for static buttons widget
        ###############
        ## img_man = BGLImageManager ( )
        ## img = img_man.load_image ( r"C:\\Users\rcarriquiryborchia\Pictures\Wip\casent0103346_d_1_high.jpg" )

        # canva = BGLCanvas(None, 0, 11, 11, 22)
        # dock = BGLRegionDock(dock_region=BGLRegionDock.DockRegion.TOP)
        # for i in range(4):
        #     dock.add_widget(BGLButton(text=str(i), height=30))
        #     l = BGLLayoutV()
        #     for j in range(3):
        #         c = BGLCheckBox(text="tototo")
        #         c.checked = lambda: bpy.context.scene.render.use_border

        #         def checked_state_changed(state):
        #             bpy.context.scene.render.use_border = state

        #         c.clicked_callback = checked_state_changed
        #         l.add_widget(c)
        #     dock.add_widget(l)

        # canva.addWidget(dock)
        # self.add_canva(canva)

    def space_type(self):
        return bpy.types.SpaceSequenceEditor

    def should_cancel(self):
        return self.context.window_manager.UAS_video_tracks_overlay is False

    def should_rebuild_ui(self) -> bool:
        props = bpy.context.scene.UAS_video_tracks_props
        if len(props.tracks) != self.track_count:
            return True
        else:
            return False


_classes = (UAS_VideoTracks_TracksOverlay,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    # bpy.types.SpaceSequenceEditor.draw_handler_add(draw_sequencer, (), "WINDOW", "POST_PIXEL")


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
    # bpy.types.SpaceSequenceEditor.draw_handler_remove(draw_sequencer, "WINDOW")

