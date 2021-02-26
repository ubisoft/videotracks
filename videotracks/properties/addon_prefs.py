import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty

from ..config import config


class UAS_VideoTracks_AddonPrefs(AddonPreferences):
    """
        Use this to get these prefs:
        prefs = context.preferences.addons["videotracks"].preferences
    """

    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package
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

    # Playblast
    ####################

    ##################################################################################
    # Draw
    ##################################################################################
    # def draw(self, context):
    #     layout = self.layout
    #     prefs = context.preferences.addons["videotracks"].preferences

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

    ##################
    # markers ###
    ##################

    # mnavbar_use_filter: BoolProperty(
    #     name="Filter Markers", default=False,
    # )

    # mnavbar_filter_text: StringProperty(
    #     name="Filter Text", default="",
    # )


_classes = (UAS_VideoTracks_AddonPrefs,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

