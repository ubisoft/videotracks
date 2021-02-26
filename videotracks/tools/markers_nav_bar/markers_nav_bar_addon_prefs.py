import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty


class UAS_markers_nav_bar_addon_prefs(AddonPreferences):
    """
        Use this to get these prefs:
        prefs = context.preferences.addons["videotracks"].preferences
    """

    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package
    # bl_idname = "__package__"
    bl_idname = "videotracks"

    ##################
    # markers ###
    ##################

    markerEmptyField: StringProperty(name=" ")

    mnavbar_use_filter: BoolProperty(
        name="Filter Markers", default=False,
    )

    mnavbar_filter_text: StringProperty(
        name="Filter Text", default="",
    )

    def _update_mnavbar_use_view_frame(self, context):
        bpy.ops.sequencer.view_frame()
        print("\n*** mnavbar_use_view_frame. New state: ", self.mnavbar_use_view_frame)

    mnavbar_use_view_frame: BoolProperty(
        name="View Frame", default=True, update=_update_mnavbar_use_view_frame,
    )


_classes = (UAS_markers_nav_bar_addon_prefs,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

