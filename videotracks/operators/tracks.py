import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, FloatVectorProperty, EnumProperty, IntProperty

from ..properties.track import UAS_VideoTracks_Track

from random import uniform


def _list_scenes(self, context):
    res = list()
    # print("Self: ", self)
    for i, scn in enumerate([c for c in bpy.data.scenes]):
        if "UAS_shot_manager_props" in scn:
            # if scn is not context.scene:  # required for camera clips use
            res.append((scn.name, scn.name, "", i))
    # if not len(res):
    #     res.append(("", "", "", 0))
    return res


def _list_takes(self, context):
    res = list()
    # print("*** self.sceneName: ", self.sceneName)
    for i, take in enumerate([c for c in bpy.data.scenes[self.sceneName].UAS_shot_manager_props.takes]):
        item = (take.name, take.name, "")
        res.append(item)
    if not len(res):
        # res = None
        res.append(("NOTAKE", "No Take Found", ""))
    #     print("Toto")
    return res


class UAS_VideoTracks_TrackAdd(Operator):
    bl_idname = "uas_video_tracks.add_track"
    bl_label = "Add New Track"
    bl_description = "Add a new track starting at the current frame" "\nThe new track is put after the selected track"
    bl_options = {"INTERNAL", "UNDO"}

    name: StringProperty(name="Name", default="New Track")
    insertAtChannel: IntProperty(name="Insert at Channel", default=1)

    color: FloatVectorProperty(
        name="Color",
        subtype="COLOR",
        size=3,
        description="Track Color",
        min=0.0,
        max=1.0,
        precision=2,
        # default=(uniform(0, 1), uniform(0, 1), uniform(0, 1)),
        default=(1.0, 1.0, 1.0),
    )

    trackType: EnumProperty(
        name="Track Type",
        description="Type of the track",
        items=(
            ("STANDARD", "Standard", ""),
            ("AUDIO", "Audio", ""),
            ("VIDEO", "Video", ""),
            ("CAM_FROM_SCENE", "Camera From Scene", ""),
            ("SHOT_CAMERAS", "Shot Manager Cameras", "Cameras from Shot Manager"),
            ("RENDERED_SHOTS", "Rendered Shots", ""),
            ("CAM_BG", "Camera Backgrounds", ""),
            ("CUSTOM", "Custom", ""),
        ),
        default="STANDARD",
        options=set(),
    )

    sceneName: EnumProperty(
        items=_list_scenes, name="Takes", description="Select a take",  # update=_current_take_changed
    )

    sceneTakeName: EnumProperty(
        items=_list_takes, name="Takes", description="Select a take",  # update=_current_take_changed
    )

    def invoke(self, context, event):
        wm = context.window_manager
        scene = context.scene
        vt_props = scene.UAS_video_tracks_props

        vt_props.updateTracksList(scene)

        # print("vt_props.selected_track_index: ", vt_props.selected_track_index)
        self.insertAtChannel = vt_props.selected_track_index + 1 if -1 < vt_props.selected_track_index else 1

        self.name = "New Track"
        self.color = (uniform(0, 1), uniform(0, 1), uniform(0, 1))

        sceneNames = _list_scenes(self, context)
        if len(sceneNames):
            self.sceneName = sceneNames[0][0]

        takeNames = _list_takes(self, context)
        if len(takeNames):
            self.sceneTakeName = (takeNames[0])[0]

        # if takeNames is not None and len(takeNames):
        #     self.sceneTakeName = takeNames[0][0]
        # else:
        #     takeNames = None

        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, row_major=True, columns=2, even_columns=False)

        col = grid_flow.column(align=False)
        col.scale_x = 0.6
        col.label(text="New Track Name:")
        col = grid_flow.column(align=False)
        col.prop(self, "name", text="")

        col = grid_flow.column(align=False)
        col.scale_x = 0.6
        col.label(text="Insert at Channel:")
        col = grid_flow.column(align=False)
        col.prop(self, "insertAtChannel", text="")

        col = grid_flow.column(align=False)
        col.label(text="Color:")
        col = grid_flow.column(align=False)
        col.prop(self, "color", text="")

        col.separator()

        col = grid_flow.column(align=False)
        col.label(text="Track Type:")
        col = grid_flow.column(align=False)
        col.prop(self, "trackType", text="")

        if "CUSTOM" != self.trackType and "STANDARD" != self.trackType:

            col.separator(factor=1.5)
            col = grid_flow.column(align=False)
            col.label(text="Scene:")
            col = grid_flow.column(align=False)
            col.prop(self, "sceneName", text="")

            col = grid_flow.column(align=False)
            col.label(text="Take:")
            col = grid_flow.column(align=False)
            #  if self.sceneTakeName == "":
            # col.alert = True
            col.prop(self, "sceneTakeName", text="")

        layout.separator()

    def execute(self, context):
        scene = context.scene
        vt_props = scene.UAS_video_tracks_props
        # selectedTrackInd = vt_props.getSelectedTrackIndex()
        # newTrackInd = vt_props.numTracks - selectedTrackInd + 1
        newTrackInd = self.insertAtChannel

        col = [self.color[0], self.color[1], self.color[2], 1]

        vt_props.addTrack(
            atIndex=newTrackInd,
            name=vt_props.getUniqueTrackName(self.name),
            color=col,
            trackType=self.trackType,
            sceneName=self.sceneName,
            sceneTakeName=self.sceneTakeName,
        )

        vt_props.setSelectedTrackByIndex(newTrackInd)

        return {"FINISHED"}


class UAS_VideoTracks_TrackDuplicate(Operator):
    bl_idname = "uas_video_tracks.duplicate_track"
    bl_label = "Duplicate Selected Track"
    bl_description = "Duplicate the track selected in the track list." "\nThe new track is put after the selected track"
    bl_options = {"INTERNAL", "UNDO"}

    name: StringProperty(name="Name")
    addToEndOfList: BoolProperty(name="Add At The End Of The List")

    @classmethod
    def poll(cls, context):
        trackList = context.scene.UAS_video_tracks_props.getTracks()
        if len(trackList) <= 0:
            return False

        return True

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, row_major=True, columns=2, even_columns=False)

        col = grid_flow.column(align=False)
        col.scale_x = 0.6
        col.label(text="New Track Name:")
        col = grid_flow.column(align=False)
        col.prop(self, "name", text="")

        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, row_major=True, columns=1, even_columns=False)
        # grid_flow.separator( factor=0.5)
        grid_flow.use_property_split = True
        grid_flow.prop(self, "startAtCurrentTime")
        grid_flow.prop(self, "addToEndOfList")

        layout.separator()

    def execute(self, context):
        vt_props = context.scene.UAS_video_tracks_props
        selectedTrack = vt_props.getSelectedTrack()
        selectedTrackInd = vt_props.getSelectedTrackIndex()

        if selectedTrack is None:
            return {"CANCELLED"}

        newTrackInd = len(vt_props.getTracks()) if self.addToEndOfList else selectedTrackInd + 1
        newTrack = vt_props.copyTrack(selectedTrack, atIndex=newTrackInd)

        newTrack.name = vt_props.getUniqueTrackName(self.name)

        vt_props.setSelectedTrackByIndex(newTrackInd)

        return {"FINISHED"}

    def invoke(self, context, event):
        #    currentTrack = context.scene.uas_video_tracks_props.getCurrentTrack()
        selectedTrack = context.scene.UAS_video_tracks_props.getSelectedTrack()
        if selectedTrack is None:
            return {"CANCELLED"}
        self.name = selectedTrack.name + "_copy"
        return context.window_manager.invoke_props_dialog(self)


class UAS_VideoTracks_MoveTrackUpDown(Operator):
    """Move items up and down in the list
    """

    bl_idname = "uas_video_tracks.move_treack_up_down"
    bl_label = "Move Track Up of Down"
    bl_description = "Move track up or down in the track stack"
    bl_options = {"INTERNAL", "UNDO"}

    action: bpy.props.EnumProperty(items=(("UP", "Up", ""), ("DOWN", "Down", "")))

    @classmethod
    def description(self, context, properties):
        descr = "_"
        if "UP" == properties.action:
            descr = "Move track up in the track stack"
        elif "DOWN" == properties.action:
            descr = "Move track down in the track stack"
        return descr

    def execute(self, context):
        scene = context.scene
        vt_props = scene.UAS_video_tracks_props
        tracks = vt_props.getTracks()
        numTracks = len(tracks)

        selectedTrackInd = vt_props.getSelectedTrackIndex()

        if self.action == "DOWN" and selectedTrackInd > 1:
            movedTrack = vt_props.moveTrackFromIndexToIndex(selectedTrackInd, selectedTrackInd - 1)
            print(f"MovedTrack: {movedTrack.name}")
            # context.window_manager.UAS_vse_render.swapChannels(
            #     scene, numTracks - selectedTrackInd, numTracks - selectedTrackInd - 1
            # )
            # tracks.move(selectedTrackInd, selectedTrackInd + 1)
            vt_props.setSelectedTrackByIndex(selectedTrackInd - 1)

        elif self.action == "UP" and selectedTrackInd < numTracks:
            movedTrack = vt_props.moveTrackFromIndexToIndex(selectedTrackInd, selectedTrackInd + 1)
            print(f"MovedTrack: {movedTrack.name}")
            # context.window_manager.UAS_vse_render.swapChannels(
            #     scene, numTracks - selectedTrackInd, numTracks - selectedTrackInd + 1
            # )
            # tracks.move(selectedTrackInd, selectedTrackInd - 1)
            vt_props.setSelectedTrackByIndex(selectedTrackInd + 1)

        return {"FINISHED"}


class UAS_VideoTracks_RemoveTrack(Operator):
    bl_idname = "uas_video_tracks.remove_track"
    bl_label = "Remove Selected Track"
    bl_description = "Remove the track selected in the track list."
    bl_options = {"INTERNAL", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.UAS_video_tracks_props.getTracks()

    def invoke(self, context, event):
        scene = context.scene
        vt_props = scene.UAS_video_tracks_props
        selectedTrackInd = vt_props.getSelectedTrackIndex()
        if 0 < selectedTrackInd:
            track = vt_props.getTrackByIndex(selectedTrackInd)
            vt_props.removeTrack(track)
            vt_props.setSelectedTrackByIndex(selectedTrackInd - 1)

        return {"FINISHED"}


class UAS_VideoTracks_TrackRemoveMultiple(Operator):
    bl_idname = "uas_video_tracks.remove_multiple_tracks"
    bl_label = "Remove Tracks"
    bl_description = "Remove the specified tracks from the list"
    bl_options = {"INTERNAL", "UNDO"}

    action: bpy.props.EnumProperty(items=(("ALL", "ALL", ""), ("DISABLED", "DISABLED", "")))

    def execute(self, context):
        scene = context.scene
        vt_props = scene.UAS_video_tracks_props
        selectedTrackInd = vt_props.getSelectedTrackIndex()

        if "ALL" == self.action:
            print("ALL in remove multiple")
            tracks = vt_props.getTracks()
            # tracks = vt_props.tracks
            print(f"tracks: {tracks}")
            for t in tracks:
                vt_props.removeTrack(t)
                tracksCheck = vt_props.getTracks()

            vt_props.setSelectedTrackByIndex(-1)

        elif "DISABLED" == self.action:
            print("DISABLED")
            tracks = vt_props.getTracks()
            for t in tracks:
                if not t.enabled:
                    vt_props.removeTrack(t)
            vt_props.setSelectedTrackByIndex(1)
        # try:
        #     item = tracks[selectedTrackInd]
        # except IndexError:
        #     pass
        # else:
        #     if self.action == "ALL":
        #         i = len(tracks) - 1
        #         while i > -1:
        #             tracks.remove(i)
        #             i -= 1
        #         vt_props.setSelectedTrackByIndex(-1)
        #     elif self.action == "DISABLED":
        #         i = len(tracks) - 1
        #         while i > -1:
        #             if not tracks[i].enabled:
        #                 tracks.remove(i)
        #             i -= 1
        #         if 0 < len(tracks):  # wkip pas parfait, on devrait conserver la sel currente
        #             vt_props.setSelectedTrackByIndex(0)

        return {"FINISHED"}


class UAS_VideoTracks_UpdateVSETrack(Operator):
    bl_idname = "uas_video_tracks.update_vse_track"
    bl_label = "Update VSE Track"
    bl_description = "Update VSE Track"
    bl_options = {"INTERNAL", "UNDO"}

    trackName: StringProperty()

    def invoke(self, context, event):

        print("trackName: ", self.trackName)
        context.scene.UAS_video_tracks_props.tracks[self.trackName].regenerateTrackContent()

        return {"FINISHED"}


class UAS_VideoTracks_ClearVSETrack(Operator):
    bl_idname = "uas_video_tracks.clear_vse_track"
    bl_label = "Clear VSE Track"
    bl_description = "Clear VSE Track"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        vt_props = context.scene.UAS_video_tracks_props
        print("trackName: ", vt_props.tracks[vt_props.selected_track_index].name)
        vt_props.tracks[vt_props.selected_track_index].clearContent()

        return {"FINISHED"}


class UAS_VideoTracks_GoToSpecifedScene(Operator):
    bl_idname = "uas_video_tracks.go_to_specified_scene"
    bl_label = "Go To Scene"
    bl_description = "Go to specified scene"
    bl_options = {"INTERNAL"}

    trackName: StringProperty()

    def invoke(self, context, event):

        print("trackName: ", self.trackName)
        # Make track scene the current one
        bpy.context.window.scene = context.scene.UAS_video_tracks_props.tracks[self.trackName].shotManagerScene
        bpy.context.window.workspace = bpy.data.workspaces["Layout"]

        return {"FINISHED"}


class UAS_VideoTracks_UpdateTracksList(Operator):
    bl_idname = "uas_video_tracks.update_tracks_list"
    bl_label = "Update Tracks List"
    bl_description = "Set a number of tracks matching the number of used channels"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        context.scene.UAS_video_tracks_props.updateTracksList(context.scene)
        return {"FINISHED"}


_classes = (
    UAS_VideoTracks_TrackAdd,
    UAS_VideoTracks_TrackDuplicate,
    UAS_VideoTracks_RemoveTrack,
    UAS_VideoTracks_MoveTrackUpDown,
    UAS_VideoTracks_TrackRemoveMultiple,
    UAS_VideoTracks_UpdateVSETrack,
    UAS_VideoTracks_ClearVSETrack,
    UAS_VideoTracks_GoToSpecifedScene,
    # UAS_VideoTracks_SetCurrentTrack,
    UAS_VideoTracks_UpdateTracksList,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)