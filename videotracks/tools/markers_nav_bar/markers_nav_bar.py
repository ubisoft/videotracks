import bpy

from videotracks.utils import utils_markers
from . import icons


def draw_markers_nav_bar_in_timeline(self, context):
    prefs = context.preferences.addons["videotracks"].preferences
    if prefs.mnavbar_display_in_timeline:
        draw_markers_nav_bar(self, context)


def draw_markers_nav_bar_in_vse(self, context):
    prefs = context.preferences.addons["videotracks"].preferences
    if prefs.mnavbar_display_in_vse:
        draw_markers_nav_bar(self, context)


def draw_markers_nav_bar(self, context):
    scene = context.scene
    prefs = context.preferences.addons["videotracks"].preferences

    layout = self.layout

    row = layout.row(align=False)
    row.separator(factor=3)
    row.alignment = "RIGHT"
    # row.label(text="toto dsf trterte")
    # row.operator("bpy.ops.time.view_all")

    # layout.label(text="Markers:")
    # box = layout.box()
    # row = box.row()
    subRow = row.row(align=True)
    subRow.operator("uas_video_tracks.go_to_marker", text="", icon="REW").goToMode = "FIRST"
    subRow.operator("uas_video_tracks.go_to_marker", text="", icon="TRIA_LEFT").goToMode = "PREVIOUS"

    subRow = row.row(align=True)
    # subRow.prop(prefs, "mnavbar_use_view_frame")
    icon = icons.icons_col["MarkersNavBar_ViewFrame_32"]
    subRow.operator(
        "uas_video_tracks.view_frame", depress=prefs.mnavbar_use_view_frame, text="", icon_value=icon.icon_id
    )

    subRow = row.row(align=True)
    subRow.operator("uas_video_tracks.go_to_marker", text="", icon="TRIA_RIGHT").goToMode = "NEXT"
    subRow.operator("uas_video_tracks.go_to_marker", text="", icon="FF").goToMode = "LAST"

    if prefs.mnavbar_display_filter:
        currentMarker = utils_markers.getMarkerAtFrame(scene, scene.frame_current)
        if currentMarker is not None:
            row.label(text=f"Marker: {currentMarker.name}")
            subRow = row.row(align=True)
            subRow.operator("uas_video_tracks.add_marker", text="", icon="SYNTAX_OFF").markerName = currentMarker.name
            subRow.operator("uas_video_tracks.delete_marker", text="", icon="X")
        else:
            row.label(text="Marker: -")
            subRow = row.row(align=True)
            subRow.operator("uas_video_tracks.add_marker", text="", icon="ADD").markerName = f"F_{scene.frame_current}"
            subSubRow = subRow.row(align=True)
            subSubRow.enabled = False
            subSubRow.operator("uas_video_tracks.delete_marker", text="", icon="X")

        subRow = row.row(align=True)
        subRow.prop(prefs, "mnavbar_use_filter", text="", icon="FILTER")
        subSubRow = subRow.row(align=True)
        subSubRow.enabled = prefs.mnavbar_use_filter
        subSubRow.prop(prefs, "mnavbar_filter_text", text="")


# _classes = (
#     UAS_VideoTracks_SetTimeRangeStart,
#     UAS_VideoTracks_SetTimeRangeEnd,
#     UAS_VideoTracks_FrameTimeRange,
# )


def register():
    # for cls in _classes:
    #     bpy.utils.register_class(cls)

    # lets add ourselves to the main header
    # bpy.types.TIME_MT_editor_menus.prepend(draw_op_item)

    bpy.types.TIME_MT_editor_menus.append(draw_markers_nav_bar_in_timeline)
    bpy.types.SEQUENCER_HT_header.append(draw_markers_nav_bar_in_vse)


#   bpy.types.TIME_HT_editor_buttons.append(draw_op_item)
# bpy.types.TIME_MT_editor_menus.append(draw_item)
# bpy.types.TIME_MT_view.append(draw_item)


def unregister():
    # for cls in reversed(_classes):
    #     bpy.utils.unregister_class(cls)

    bpy.types.TIME_MT_editor_menus.remove(draw_markers_nav_bar_in_timeline)
    bpy.types.SEQUENCER_HT_header.remove(draw_markers_nav_bar_in_vse)


# if __name__ == "__main__":
#     register()

#     # The menu can also be called from scripts
#     bpy.ops.wm.call_menu(name=MyCustomMenu.bl_idname)
