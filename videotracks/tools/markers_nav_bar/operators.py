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
                bpy.ops.sequencer.view_frame()

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


_classes = (
    UAS_VideoTracks_GoToMarker,
    UAS_VideoTracks_AddMarker,
    UAS_VideoTracks_DeleteMarker,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
