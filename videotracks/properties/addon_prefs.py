import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty

from ..config import config

from videotracks.tools.markers_nav_bar.markers_nav_bar_addon_prefs import draw_markers_nav_bar_settings
from videotracks.tools.time_controls_bar.time_controls_bar_addon_prefs import draw_time_controls_bar_settings


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

    ##################
    # ui helpers   ###
    ##################

    # used for example as a placehoder in VSM to have a text field when no strip is selected
    emptyField: StringProperty(name=" ")
    emptyBool: BoolProperty(name=" ", default=False)

    ##################
    # global temps values   ###
    ##################

    ##################
    # Markers Nav Bar Settings ###
    ##################

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

        draw_markers_nav_bar_settings(self, context, box)
        draw_time_controls_bar_settings(self, context, box)

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

    # layout.label(
    #     text="Temporary preference values (for dialogs for instance) are only visible when global variable uasDebug is True."
    # )

    # if config.uasDebug:
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

