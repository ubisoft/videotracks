# -*- coding: utf-8 -*-
import bpy, bgl, blf, gpu
from gpu_extras.batch import batch_for_shader


def get_rectangle_region_coordinates(rectangle=(0, 0, 5, 5), view_boundaries=(0, 0, 1920, 1080)):
    """Calculates strip coordinates in region's pixels norm, clamped into region

    :param rectangle: Rectangle to get coordinates of
    :param view_boundaries: Cropping area
    :return: Strip coordinates in region's pixels norm, resized for status color bar
    """
    region = bpy.context.region

    # Converts x and y in terms of the grid's frames and channels to region pixels coordinates clamped
    x1, y1 = region.view2d.view_to_region(
        max(view_boundaries[0], min(rectangle[0], view_boundaries[2])),
        max(view_boundaries[1], min(rectangle[1], view_boundaries[3])),
    )
    x2, y2 = region.view2d.view_to_region(
        max(view_boundaries[0], min(rectangle[2], view_boundaries[2])),
        max(view_boundaries[1], min(rectangle[3], view_boundaries[3])),
    )

    return x1, y1, x2, y2


def build_rectangle(coordinates, indices=((0, 1, 2), (2, 1, 3))):
    """Build an OpenGL rectangle into region

    :param coordinates: Four points coordinates
    :param indices: Rectangle's indices
    :return: Built vertices and indices
    """
    # Building the Rectangle
    vertices = (
        (coordinates[0], coordinates[1]),
        (coordinates[2], coordinates[1]),
        (coordinates[0], coordinates[3]),
        (coordinates[2], coordinates[3]),
    )

    return vertices, indices


def draw_rect(rect_width, shader, i, view_boundaries):
    region = bpy.context.region
    x_view_fixed, y_view_fixed = region.view2d.region_to_view(20, 50)

    # Build track rectangle
    track_rectangle = get_rectangle_region_coordinates((x_view_fixed, i + 1, x_view_fixed, i + 2), view_boundaries)

    vertices, indices = build_rectangle(
        (track_rectangle[0], track_rectangle[1], track_rectangle[2] + rect_width, track_rectangle[3],)
    )

    # Draw the rectangle
    batch = batch_for_shader(shader, "TRIS", {"pos": vertices}, indices=indices)
    batch.draw(shader)


def draw_channel_name(tracks, view_boundaries):
    """Draw tracks name

    :param view_boundaries: View boundaries
    """
    region = bpy.context.region
    font_id = 0

    x_view_fixed, y_view_fixed = region.view2d.region_to_view(20, 50)
    width_track_frame_fixed = 150
    shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")
    shader.bind()

    # Draw track rectangles
    bgl.glEnable(bgl.GL_BLEND)  # Enables alpha channel
    dark_track = False
    for i, track in enumerate(reversed(tracks)):  # Out of text loop because of OpenGL issue, rectangles are bugging
        # shader.uniform_float("color", (0.66, 0.66, 0.66, 0.7))
        shader.uniform_float("color", (track.color[0], track.color[1], track.color[2], 0.7))

        # Alternate track color
        # if dark_track:
        #     shader.uniform_float("color", (0.5, 0.5, 0.5, 0.7))
        # dark_track = not dark_track

        draw_rect(width_track_frame_fixed, shader, i, view_boundaries)

        # draw selected rect
        vt_props = bpy.context.scene.UAS_video_tracks_props
        currentTrackInd = vt_props.getSelectedTrackIndex()
        if i + 1 == currentTrackInd:
            # shader.uniform_float("color", (0.5, 0.2, 0.2, 0.2))
            shader.uniform_float("color", (track.color[0], track.color[1], track.color[2], 0.15))
            draw_rect(1800, shader, i, view_boundaries)

        # # Build track rectangle
        # track_rectangle = get_rectangle_region_coordinates((x_view_fixed, i + 1, x_view_fixed, i + 2), view_boundaries)

        # vertices, indices = build_rectangle(
        #     (track_rectangle[0], track_rectangle[1], track_rectangle[2] + width_track_frame_fixed, track_rectangle[3],)
        # )

        # # Draw the rectangle
        # batch = batch_for_shader(shader, "TRIS", {"pos": vertices}, indices=indices)
        # batch.draw(shader)

    # Display text
    for i, track in enumerate(reversed(tracks)):
        x, y = region.view2d.view_to_region(x_view_fixed, i + 1.4)

        blf.position(font_id, 30, y, 0)
        blf.size(font_id, 12, 72)
        blf.color(font_id, 1, 1, 1, 0.9)
        blf.draw(font_id, track.name)

        i += 1


def draw_sequencer():
    """Draw sequencer OpenGL"""
    # if True == True:
    # return ()
    # Sentinel if no sequences, abort
    # if not hasattr(bpy.context.scene.sequence_editor, "sequences"):
    #     return
    props = bpy.context.scene.UAS_video_tracks_props
    region = bpy.context.region

    # Defining boundaries of the area to crop rectangles in view pixels' space
    x_view_min, y_view_min = region.view2d.region_to_view(0, 11)
    x_view_max, y_view_max = region.view2d.region_to_view(region.width - 11, region.height - 22)
    view_boundaries = (x_view_min, y_view_min, x_view_max, y_view_max)

    draw_channel_name(props.tracks, view_boundaries)


from .bgl_ui import BGL_UIOperatorBase, BGLCanvas
from .bgl_ui.widgets import *
from .bgl_ui.geometry import *
from .bgl_ui.types import BGLViewToRegion


class UAS_VideoTracks_TracksOverlay ( BGL_UIOperatorBase ):
    bl_idname = "uas_video_tracks.tracks_overlay"
    bl_label = "Draw tracks overlay."
    bl_options = { "REGISTER", "INTERNAL" }

    def __init__ ( self ):
        BGL_UIOperatorBase.__init__ ( self )

    def build_ui( self ):
        props = bpy.context.scene.UAS_video_tracks_props
        self.track_count = len ( props.tracks ) # used for rebuilding ui

        canva = BGLCanvas ( BGLViewToRegion ( ), 0, 11, 11, 22 )
        self.add_canva ( canva )
        size = 100000

        b = BGLRect ( size, size * 2 )
        b.color = BGLColor ( 1, 0, 0, .75 )
        frame_range_left = BGLGeometryStamp ( lambda: BGLCoord ( -size + bpy.context.scene.frame_start, -size ), b )

        b = BGLRect ( size, size * 2 )
        b.color = BGLColor ( 1, 0, 0, .75 )
        frame_range_right = BGLGeometryStamp ( lambda: BGLCoord ( bpy.context.scene.frame_end, -size ), b )
        canva.addWidget ( frame_range_left )
        canva.addWidget ( frame_range_right )

        canva = BGLCanvas ( BGLViewToRegion ( apply_to_x = False ), 0, 11, 11, 22 )
        self.add_canva ( canva )

        rect = BGLRect ( 9999999, 1 )
        track_selected_frame = BGLGeometryStamp ( lambda prop =  props: BGLCoord ( 0, prop.selected_track_index ), rect )
        rect.color = lambda prop = props: BGLColor ( prop.tracks[prop.selected_track_index_inverted].color[ 0 ],
                                                                     prop.tracks[prop.selected_track_index_inverted].color[ 1 ],
                                                                     prop.tracks[prop.selected_track_index_inverted].color[ 2 ], .5 )
        canva.addWidget ( track_selected_frame )

        for i, track in enumerate(reversed(props.tracks)):
            pos = BGLCoord ( 0, i + 1 )
            button = BGLButton ( pos, 100, 1, lambda track=track: track.name )
            button.clicked_callback = lambda prop = props, index = i: prop.setSelectedTrackByIndex ( index + 1 )
            button.color = lambda track = track: BGLColor ( track.color[ 0 ], track.color[ 1 ], track.color[ 2 ] )
            canva.addWidget ( button )

            slider = BGLSlider ( pos, 100, .2 )
            slider.value = lambda t = track: t.opacity
            def update_opacity ( v, t = track ): t.opacity = v
            slider.on_value_changed = update_opacity
            canva.addWidget ( slider )
            

        img_man = BGLImageManager ( )
        img = img_man.load_image ( r"C:\\Users\rcarriquiryborchia\Pictures\Wip\casent0103346_d_1_high.jpg" )


    def space_type ( self ):
        return bpy.types.SpaceSequenceEditor

    def should_cancel ( self ):
        return False

    def should_rebuild_ui( self ) -> bool:
        props = bpy.context.scene.UAS_video_tracks_props
        if len ( props.tracks ) != self.track_count:
            return True
        else:
            return False



_classes = ( UAS_VideoTracks_TracksOverlay, )

def register():
    for cls in _classes:
        bpy.utils.register_class ( cls )
    #bpy.types.SpaceSequenceEditor.draw_handler_add(draw_sequencer, (), "WINDOW", "POST_PIXEL")


def unregister():
    for cls in reversed ( _classes ):
        bpy.utils.unregister_class ( cls )
    #bpy.types.SpaceSequenceEditor.draw_handler_remove(draw_sequencer, "WINDOW")
