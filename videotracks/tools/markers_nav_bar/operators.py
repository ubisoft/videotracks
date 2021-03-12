import bpy
from bpy.types import Operator
from bpy.props import StringProperty

from videotracks.utils import utils_markers

####################
# Markers
####################


class UAS_VideoTracks_GoToMarker(Operator):
    bl_idname = "uas_video_tracks.go_to_marker"
    bl_label = "Go To Marker"
    bl_description = "Go to the specified marker"
    bl_options = {"INTERNAL"}

    goToMode: StringProperty(
        name="Go To Mode", description="Go to the specified marker. Can be FIRST, PREVIOUS, NEXT, LAST", default="NEXT"
    )

    def invoke(self, context, event):
        scene = context.scene
        prefs = context.preferences.addons["videotracks"].preferences
        marker = None

        filterText = "" if not prefs.mnavbar_use_filter else prefs.mnavbar_filter_text

        if len(scene.timeline_markers):
            # print(self.goToMode)
            if "FIRST" == self.goToMode:
                marker = utils_markers.getFirstMarker(scene, scene.frame_current, filter=filterText)
            elif "PREVIOUS" == self.goToMode:
                marker = utils_markers.getMarkerBeforeFrame(scene, scene.frame_current, filter=filterText)
            elif "NEXT" == self.goToMode:
                marker = utils_markers.getMarkerAfterFrame(scene, scene.frame_current, filter=filterText)
            elif "LAST" == self.goToMode:
                marker = utils_markers.getLastMarker(scene, scene.frame_current, filter=filterText)

            if marker is not None:
                scene.frame_set(marker.frame)

            if prefs.mnavbar_use_view_frame:
                try:
                    bpy.ops.sequencer.view_frame()
                except Exception as e:
                    # context is timeline, not VSE
                    pass

        return {"FINISHED"}


class UAS_VideoTracks_AddMarker(Operator):
    bl_idname = "uas_video_tracks.add_marker"
    bl_label = "Add / Rename Marker"
    bl_description = "Add or rename a marker at the specified frame"
    bl_options = {"INTERNAL", "UNDO"}

    markerName: StringProperty(name="New Marker Name", default="")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        utils_markers.addMarkerAtFrame(context.scene, context.scene.frame_current, self.markerName)
        return {"FINISHED"}


class UAS_VideoTracks_DeleteMarker(Operator):
    bl_idname = "uas_video_tracks.delete_marker"
    bl_label = "Delete Marker"
    bl_description = "Delete the marker at the specified frame"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        utils_markers.deleteMarkerAtFrame(context.scene, context.scene.frame_current)
        return {"FINISHED"}


class UAS_VideoTracks_ViewFrame(Operator):
    bl_idname = "uas_video_tracks.view_frame"
    bl_label = "View Frame"
    bl_description = """Reframe the time range displayed into the timeline to preverse the visibility of the time cursor.
    \nAdditional settings are located in the Video Tracks add-on preferences, in the Preferences panel"""
    bl_options = {"INTERNAL"}
    """This operator provides a more useful control of the framing than just using the property prefs.mnavbar_use_view_frame
    """

    def invoke(self, context, event):
        prefs = context.preferences.addons["videotracks"].preferences
        if not prefs.mnavbar_use_view_frame:
            if prefs.mnavbar_use_view_frame:
                try:
                    bpy.ops.sequencer.view_frame()
                except Exception as e:
                    # context is timeline, not VSE
                    pass
        prefs.mnavbar_use_view_frame = not prefs.mnavbar_use_view_frame
        return {"FINISHED"}


_classes = (
    UAS_VideoTracks_GoToMarker,
    UAS_VideoTracks_AddMarker,
    UAS_VideoTracks_DeleteMarker,
    UAS_VideoTracks_ViewFrame,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
