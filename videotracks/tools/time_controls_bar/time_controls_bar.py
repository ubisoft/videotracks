import bpy

from videotracks.utils import utils_markers
from . import icons


def draw_time_controls_bar_in_timeline(self, context):
    prefs = context.preferences.addons["videotracks"].preferences
    if prefs.tcbar_display_in_timeline:
        draw_time_controls_bar(self, context)


def draw_time_controls_bar_in_vse(self, context):
    prefs = context.preferences.addons["videotracks"].preferences
    if prefs.tcbar_display_in_vse:
        draw_time_controls_bar(self, context)


def draw_time_controls_bar(self, context):
    scene = context.scene
    prefs = context.preferences.addons["videotracks"].preferences

    layout = self.layout

    row = layout.row(align=False)
    row.separator(factor=3)
    row.alignment = "RIGHT"
    # row.label(text="toto dsf trterte")
    # row.operator("bpy.ops.time.view_all")

    row.operator("time_controls_bar.set_time_range_start", text="", icon="TRIA_UP_BAR")
    row.operator("time_controls_bar.frame_time_range", text="", icon="CENTER_ONLY")
    row.operator("time_controls_bar.set_time_range_end", text="", icon="TRIA_UP_BAR")


# _classes = (
#     TimeControl_SetTimeRangeStart,
#     TimeControl_SetTimeRangeEnd,
#     UAS_VideoTracks_FrameTimeRange,
# )


def register():
    # for cls in _classes:
    #     bpy.utils.register_class(cls)

    # lets add ourselves to the main header
    # bpy.types.TIME_MT_editor_menus.prepend(draw_op_item)

    bpy.types.TIME_MT_editor_menus.append(draw_time_controls_bar_in_timeline)
    bpy.types.SEQUENCER_HT_header.append(draw_time_controls_bar_in_vse)


#   bpy.types.TIME_HT_editor_buttons.append(draw_op_item)
# bpy.types.TIME_MT_editor_menus.append(draw_item)
# bpy.types.TIME_MT_view.append(draw_item)


def unregister():
    # for cls in reversed(_classes):
    #     bpy.utils.unregister_class(cls)

    bpy.types.TIME_MT_editor_menus.remove(draw_time_controls_bar_in_timeline)
    bpy.types.SEQUENCER_HT_header.remove(draw_time_controls_bar_in_vse)


# if __name__ == "__main__":
#     register()

#     # The menu can also be called from scripts
#     bpy.ops.wm.call_menu(name=MyCustomMenu.bl_idname)
