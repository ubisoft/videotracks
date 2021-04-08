import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty


def draw_time_controls_bar_settings(self, context, layout):
    prefs = context.preferences.addons["videotracks"].preferences

    row = layout.row()
    row.separator()
    box = row.box()

    row = box.row(align=False)
    row.separator()
    row.prop(prefs, "tcbar_display_in_vse")

    row = box.row(align=False)
    row.separator()
    row.prop(prefs, "tcbar_display_in_timeline")


####################
# Following code has been moved to addon-prefs.py because it wasn't possible to create additionnal add-on
# properties in several modules
####################

# class UAS_markers_nav_bar_addon_prefs(AddonPreferences):
#     """
#         Use this to get these prefs:
#         prefs = context.preferences.addons["videotracks"].preferences
#     """

#     # this must match the add-on name, use '__package__'
#     # when defining this in a submodule of a python package
#     # bl_idname = "__package__"
#     bl_idname = __package__
#     # bl_idname = "videotracks"

#     ##################
#     # Settings ###
#     ##################

#     mnavbar_display_in_vse: BoolProperty(
#         name="Display in VSE", description="Display Markers Nav Bar in the VSE toolbar", default=True,
#     )
#     mnavbar_display_filter: BoolProperty(
#         name="Display Filter", description="Display the filter tools", default=True,
#     )

#     ##################
#     # Component controls ###
#     ##################

#     markerEmptyField: StringProperty(name=" ")

#     mnavbar_use_filter: BoolProperty(
#         name="Filter Markers", default=False,
#     )

#     mnavbar_filter_text: StringProperty(
#         name="Filter Text", default="",
#     )

#     def _update_mnavbar_use_view_frame(self, context):
#         if self.mnavbar_use_view_frame:
#             bpy.ops.sequencer.view_frame()
#         print("\n*** mnavbar_use_view_frame. New state: ", self.mnavbar_use_view_frame)

#     mnavbar_use_view_frame: BoolProperty(
#         name="View Frame", default=True, update=_update_mnavbar_use_view_frame,
#     )


# _classes = (UAS_markers_nav_bar_addon_prefs,)
_classes = ()


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

