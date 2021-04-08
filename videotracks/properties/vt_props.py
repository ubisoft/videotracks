# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
To do: module description here.
"""

import bpy
from bpy.types import Scene
from bpy.types import PropertyGroup
from bpy.props import (
    CollectionProperty,
    IntProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    PointerProperty,
)

from videotracks.properties.track import UAS_VideoTracks_Track

from videotracks.utils import utils
from videotracks.utils import utils_vse

import logging

_logger = logging.getLogger(__name__)


class VideoTracks_Props(PropertyGroup):
    def version(self):
        """ Return the add-on version in the form of a tupple made by: 
                - a string x.y.z (eg: "1.21.3")
                - an integer. x.y.z becomes xxyyyzzz (eg: "1.21.3" becomes 1021003)
            Return None if the addon has not been found
        """
        return utils.addonVersion("UAS Video Tracks")

    def initialize_video_shot_manager(self):
        print(f"\nInitializing Video Tracks... Scene: {bpy.context.scene.name}")
        # self.parentScene = self.getParentScene()

        if self.parentScene is None:
            self.parentScene = self.findParentScene()
        # _logger.info(f"\n  self.parentScene : {self.parentScene}")

        # self.initialize()
        # self.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
        # self.createDefaultTake()
        # self.createRenderSettings()
        self.updateTracksList(self.parentScene)  # bad context
        bpy.ops.uas_video_tracks.tracks_overlay ( "INVOKE_DEFAULT" )
        self.isInitialized = True

    def get_isInitialized(self):
        #    print(" get_isInitialized")
        val = self.get("isInitialized", False)

        if not val:
            self.initialize_video_shot_manager()

        return val

    def set_isInitialized(self, value):
        #  print(" set_isInitialized: value: ", value)
        self["isInitialized"] = value

    isInitialized: BoolProperty(get=get_isInitialized, set=set_isInitialized, default=False)

    parentScene: PointerProperty(type=Scene,)  # get=_get_parentScene, set=_set_parentScene,

    def getParentScene(self):
        parentScn = None
        try:
            parentScn = self.parentScene
        except Exception:  # as e
            print("Error - parentScene property is None in vt_props.getParentScene():", sys.exc_info()[0])

        # if parentScn is not None:
        #     return parentScn
        if parentScn is None:
            _logger.error("\n\n WkError: parentScn in None in Props !!! *** ")
            self.parentScene = self.findParentScene()
        else:
            self.parentScene = parentScn

        if self.parentScene is None:
            print("\n\n Re WkError: self.parentScene in still None in Props !!! *** ")
        # findParentScene is done in initialize function

        return self.parentScene

    def findParentScene(self):
        for scn in bpy.data.scenes:
            if "UAS_video_tracks_props" in scn:
                props = scn.UAS_video_tracks_props
                if self == props:
                    #    print("findParentScene: Scene found")
                    return scn
        # print("findParentScene: Scene NOT found")
        return None

    def _get_numTracks(self):
        val = self.get("numTracks", 0)
        val = len(self.tracks)
        return val

    def _set_numTracks(self, value):
        # new tracks are added at the top
        if value > len(self.tracks):
            v = value
            while v > len(self.tracks):
                atIndex = len(self.tracks) + 1
                self.addTrack(mode="HEADER", name=f"Track {atIndex}", trackType="STANDARD", atIndex=atIndex)
            self["numTracks"] = value
        else:
            self["numTracks"] = len(self.tracks)

    def _update_numTracks(self, context):

        # while self.numTracks > len(self.tracks):
        #     self.addTrack(trackType="STANDARD",)
        pass

    numTracks: IntProperty(
        name="Num Tracks",
        min=0,
        soft_max=20,
        max=32,
        get=_get_numTracks,
        set=_set_numTracks,
        update=_update_numTracks,
        default=5,
    )

    tracks: CollectionProperty(type=UAS_VideoTracks_Track)

    # property used by the template_list component in an inverted order than selected_track_index in order
    # to reflect the VSE channels stack
    def _get_selected_track_index_inverted(self):
        val = self.get("selected_track_index_inverted", -1)
        return val

    def _set_selected_track_index_inverted(self, value):
        self["selected_track_index_inverted"] = value

    # self.selected_track_index = len(self.tracks) - self["selected_track_index_inverted"]

    def _update_selected_track_index_inverted(self, context):
        if self.selected_track_index != len(self.tracks) - self["selected_track_index_inverted"]:
            self.selected_track_index = len(self.tracks) - self["selected_track_index_inverted"]

    #    print("\n*** _update_selected_track_index_inverted updated. New state: ", self.selected_track_index_inverted)

    # Works from 0 to len(self.track) - 1
    selected_track_index_inverted: IntProperty(
        name="Selected Track Index Inverted",
        get=_get_selected_track_index_inverted,
        set=_set_selected_track_index_inverted,
        update=_update_selected_track_index_inverted,
        default=-1,
    )

    def _get_selected_track_index(self):
        val = self.get("selected_track_index", -1)
        return val

    def _set_selected_track_index(self, value):
        self["selected_track_index"] = value

    def _update_selected_track_index(self, context):
        #    print("\n*** _update_selected_track_index updated. New state: ", self.selected_track_index)
        if self.selected_track_index_inverted != len(self.tracks) - self["selected_track_index"]:
            self.selected_track_index_inverted = len(self.tracks) - self["selected_track_index"]

    # Really represent the track (or channel) index. Then goes from 1 to number of tracks
    selected_track_index: IntProperty(
        name="Selected Track Index",
        get=_get_selected_track_index,
        set=_set_selected_track_index,
        update=_update_selected_track_index,
        default=-1,
    )

    display_color_in_tracklist: BoolProperty(name="Display Color in Track List", default=True, options=set())
    display_opacity_or_volume_in_tracklist: BoolProperty(
        name="Display Opacity in Track List", default=True, options=set()
    )
    display_track_type_in_tracklist: BoolProperty(name="Display Track Type in Track List", default=False, options=set())

    def _filter_jumpToScene(self, object):
        """ Return true only for cameras from the same scene as the shot
        """
        # print("self", str(self))  # this shot
        # print("object", str(object))  # all the objects of the property type

        # if object.type == "SCENE" and object.name in self.parentScene.objects:
        if object is bpy.context.scene:
            return False
        else:
            return True

    jumpToScene: PointerProperty(
        name="Jump To Scene", description="Scene to go to", type=bpy.types.Scene, poll=_filter_jumpToScene,
    )

    ####################
    # tracks
    ####################

    def getUniqueTrackName(self, nameToMakeUnique):
        uniqueName = nameToMakeUnique

        trackList = self.getTracks()

        dup_name = False
        for track in trackList:
            if uniqueName == track.name:
                dup_name = True
        if dup_name:
            uniqueName = f"{uniqueName}_1"

        return uniqueName

    def addTrack(
        self,
        mode="CHANNEL_AND_HEADER",
        atIndex=-1,
        name="defaultTrack",
        start=10,
        end=20,
        camera=None,
        color=None,
        enabled=True,
        trackType="STANDARD",
        sceneName="",
        sceneTakeName="",
    ):
        """ Add a new track after the selected track if possible or at the end of the track list otherwise
            Return the newly added track
            mode can be: "CHANNEL_AND_HEADER", "CHANNEL", "HEADER"
        """

        newTrack = None

        if "CHANNEL_AND_HEADER" == mode or "HEADER" == mode:
            trackListInverted = self.tracks

            newTrack = trackListInverted.add()  # track is added at the end
            newTrack.parentScene = self.getParentScene()
            # print(f"****Add Track: newTrack.parentScene: {newTrack.parentScene}")
            newTrack.name = name
            newTrack.enabled = enabled
            newTrack.trackType = trackType

            if color is None:
                newTrack.setColorFromTrackType()

            else:
                newTrack.color = color

            if "" != sceneName:
                newTrack.shotManagerScene = bpy.data.scenes[sceneName]
            if "" != sceneTakeName:
                newTrack.sceneTakeName = sceneTakeName

            if -1 != atIndex:  # move track at specified index
                # trackListInverted.move(len(trackList) - 1, len(trackList) - atIndex)
                trackListInverted.move(len(trackListInverted) - 1, len(trackListInverted) - atIndex)
                newTrack = trackListInverted[len(trackListInverted) - atIndex]

        if "CHANNEL_AND_HEADER" == mode or "CHANNEL" == mode:
            utils_vse.insertChannel(self.parentScene, atIndex)

        return newTrack

    def copyTrack(self, track, mode="CHANNEL_AND_HEADER", atIndex=-1, toIndex=-1):
        """ Copy a track after the selected track if possible or at the end of the track list otherwise
            Return the newly added track
        """
        print(f"copyTrack: mode: {mode}")
        newTrack = None
        if "CHANNEL_AND_HEADER" == mode or "HEADER" == mode:
            trackListInverted = self.tracks

            newTrack = trackListInverted.add()  # track is added at the end
            newTrack.parentScene = track.parentScene
            print(f"---Track source: {track.parentScene}, track copy:{newTrack.parentScene}")
            newTrack.name = track.name
            newTrack.enabled = track.enabled
            newTrack.color = track.color

            if -1 != toIndex:  # move track at specified index
                # trackList.move(len(trackListInverted) - 1, atIndex)
                trackListInverted.move(len(trackListInverted) - 1, len(trackListInverted) - toIndex)
                newTrack = trackListInverted[len(trackListInverted) - toIndex]

        if "CHANNEL_AND_HEADER" == mode or "CHANNEL" == mode:
            # toIndex = atIndex + 1
            utils_vse.duplicateChannel(self.parentScene, atIndex, toIndex)

        return newTrack

    def removeTrack(
        self, track, mode="CHANNEL_AND_HEADER",
    ):
        trackInd = self.getTrackIndex(track)
        if "CHANNEL_AND_HEADER" == mode or "HEADER" == mode:
            print(f"Remove TRack: Name: {track.name} at {trackInd}")
            utils_vse.clearChannel(self.parentScene, trackInd)
            trackListInverted = self.tracks
            trackListInverted.remove(len(trackListInverted) - trackInd)

        if "CHANNEL_AND_HEADER" == mode or "CHANNEL" == mode:
            utils_vse.removeChannel(self.parentScene, trackInd)

    def setTrackInfo(
        self,
        trackIndex,
        name=None,
        start=None,
        end=None,
        camera=-1,
        color=None,
        enabled=None,
        trackType=None,
        sceneName=None,
        sceneTakeName=None,
    ):
        """ Set the information of an existing track
            Returns the track
        """
        track = None
        trackList = self.getTracks()

        if not 0 <= trackIndex - 1 < len(trackList):
            return track
        track = trackList[trackIndex - 1]

        if name is not None:
            track.name = name

        if enabled is not None:
            track.enabled = enabled

        if trackType is not None:
            track.trackType = trackType

        if color is not None:
            track.color = color

        # if "" != sceneName:
        #     newTrack.shotManagerScene = bpy.data.scenes[sceneName]
        # if "" != sceneTakeName:
        #     newTrack.sceneTakeName = sceneTakeName

        # if -1 != atIndex:  # move track at specified index
        #     trackList.move(len(trackList) - 1, len(trackList) - atIndex)

        # #  self.numTracks += 1

        return track

    def getTrackIndex(self, track):
        trackList = self.getTracks()
        for i in range(len(trackList)):
            if track == trackList[i]:
                return i + 1
        return -1
        # trackInd = -1

        # trackList = self.getTracks()

        # trackInd = 0
        # while trackInd < len(trackList) and track != trackList[trackInd]:  # wkip mettre trackList[trackInd].name?
        #     trackInd += 1
        # if trackInd == len(trackList):
        #     trackInd = -1

        # return trackInd

    def moveTrackFromIndexToIndex(
        self, fromIndex, toIndex, mode="CHANNEL_AND_HEADER",
    ):
        newTrack = None
        if "CHANNEL_AND_HEADER" == mode or "HEADER" == mode:
            trackListInverted = self.tracks
            trackListInverted.move(len(trackListInverted) - fromIndex, len(trackListInverted) - toIndex)
            newTrack = trackListInverted[len(trackListInverted) - toIndex]
        else:
            newTrack = self.getTrackByIndex(fromIndex)

        if "CHANNEL_AND_HEADER" == mode or "CHANNEL" == mode:
            utils_vse.swapChannels(self.parentScene, fromIndex, toIndex)

        return newTrack

    def getTrackByIndex(self, trackIndex):
        if not (0 < trackIndex <= len(self.tracks)):
            return None
        return self.getTracks()[trackIndex - 1]

    def getTrackByName(self, trackName):
        for t in self.tracks:
            if t.name == trackName:
                return t
        return None

    def getTracks(self, ignoreDisabled=False):
        """Return a list of tracks inverted from the one stored internally. This is because tracks are directly used by the
            template list ui component.
            The list starts at 0 and ends at number of channels - 1
        """
        return [t for t in reversed(self.tracks) if not ignoreDisabled or t.enabled]

    # def getTracksList(self, ignoreDisabled=False):
    #     trackList = []

    #     for track in self.tracks:
    #         if not ignoreDisabled or track.enabled:
    #             trackList.append(track)

    #     return trackList

    def getSelectedTrackIndex(self):
        """ Return the index of the selected track in the enabled track list
            Use this function instead of a direct call to self.selected_track_index
        """
        if 0 >= len(self.getTracks()):
            self.selected_track_index = -1

        return self.selected_track_index

    def getSelectedTrack(self):
        selTrackInd = self.getSelectedTrackIndex()
        if 0 >= selTrackInd:
            return None
        trackList = self.getTracks()
        return trackList[selTrackInd - 1]
        # selectedTrackInd = self.getSelectedTrackIndex()
        # selectedTrack = None
        # if -1 != selectedTrackInd:
        #     selectedTrack = (self.getTracks())[selectedTrackInd]

        # return selectedTrack

    def setSelectedTrackByIndex(self, selectedTrackIndex):
        # print("setSelectedTrackByIndex: selectedTrackIndex:", selectedTrackIndex)
        self.selected_track_index = selectedTrackIndex

    def setSelectedTrack(self, selectedTrack):
        trackInd = self.getTrackIndex(selectedTrack)
        self.setSelectedTrackByIndex(trackInd)

    def updateTracksList(self, scene):
        """Add new track at the top of the list
        """
        # numChannels = utils_vse.getNumUsedChannels(self.parentScene)

        # if self.numTracks < numChannels:
        #     self.numTracks = numChannels

        if 32 > self.numTracks:
            self.numTracks = 32

    ####################
    # channels
    ####################

    def getChannelClips(self, channelIndex):
        clipsList = list()
        for seq in self.parentScene.sequence_editor.sequences:
            if channelIndex == seq.channel:
                clipsList.append(seq)

        return clipsList

    def getChannelClipsNumber(self, channelIndex):
        clipsList = self.getChannelClips(channelIndex)
        return len(clipsList)


_classes = (
    UAS_VideoTracks_Track,
    VideoTracks_Props,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.UAS_video_tracks_props = PointerProperty(type=VideoTracks_Props)


def unregister():

    del bpy.types.Scene.UAS_video_tracks_props

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
