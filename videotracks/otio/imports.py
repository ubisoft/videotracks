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

import os
from pathlib import Path
from urllib.parse import unquote_plus, urlparse
import re

import bpy
import opentimelineio

from videotracks.utils import utils

from . import otio_wrapper as ow

import logging

_logger = logging.getLogger(__name__)


def importTrack(track, trackInd, track_type, timeRange=None, offsetFrameNumber=0, alternative_media_folder=""):
    verbose = False
    #   verbose = "VIDEO" == track_type

    trackInfo = "\n\n------------------------------------------------------------"
    trackInfo += "\n------------------------------------------------------------"
    trackInfo += "\n  - Track {trackInd}: {track.name}, {track_type}"

    range_start = -9999999
    range_end = 9999999
    fps = 25
    if timeRange is not None:
        range_start = timeRange[0]
        range_end = timeRange[1]
        trackInfo += f" - import from {range_start} to {range_end} (included)"
    if verbose:
        print(f"{trackInfo}")

    for i, clip in enumerate(track.each_clip()):
        # if 5 < i:
        #    break
        clip_start = ow.get_clip_frame_final_start(clip, fps)
        clip_end = ow.get_timeline_clip_end_inclusive(clip)

        clipInfo = "\n\n- *** ----------------------------"
        clipInfo += f"\n  - Clip name: {clip.name}, Clip ind: {i}"

        isInRange = utils.segment_is_in_range(clip_start, clip_end, range_start, range_end, partly_inside=True)

        # excluse media out of range
        if not isInRange:
            # excludInfo = " not in range"
            # print(f"{excludInfo}")
            continue

        media_path = Path(ow.get_clip_media_path(clip))

        # possibly excluse some media types
        # mediaExt = Path(media_path).suffix
        # if mediaExt == ".wav":
        #     excludInfo = "    ** Media exluded: "
        #     continue

        clipInfo += f", media: {media_path}"
        # clipInfo += f"\n  -   metadata:{clip.metadata['fcp_xml']}\n"
        clipInfo += f"\n  -   metadata:{clip.metadata}\n"
        if verbose:
            print(f"{clipInfo}")
            print(f"clip_start: {clip_start}, clip_end: {clip_end}, range_start: {range_start}, range_end: {range_end}")
            # _logger.debug(f"{clipInfo}")

            # print(f"{clip}")
            #   print(f"       Import Otio media_path: {media_path}")

            # print(f"{clipInfo}")
            # print(f"{clip}")

            # print("       Clip is in range")
            #    print(f"{clipInfo}")
            # offsetFrameNumber = 2
            #    _logger.debug(f"media_path: {media_path}")
            print(f"       Import at frame: offsetFrameNumber: {offsetFrameNumber}")
        if not media_path.exists():
            print(f"    *** Media not found: {media_path}")
            # Lets find it inside next to the xml
            # media_path = Path(otioFile).parent.joinpath(media_path.name)
            media_path = Path(alternative_media_folder).joinpath(media_path.name)
            _logger.debug(f'** media not found, so using alternative_media_folder: "{alternative_media_folder}"')
            _logger.debug(f"   and new media_path: {media_path}")

        if not media_path.exists():
            print(f"    *** Media still not found: {media_path}")
        else:
            media_path = str(media_path)

            # start = ow.get_clip_frame_final_start(clip) + offsetFrameNumber
            start = opentimelineio.opentime.to_frames(clip.range_in_parent().start_time)
            end = ow.get_timeline_clip_end_inclusive(clip) + offsetFrameNumber
            availableRange = clip.available_range()
            # _logger.debug(f"  clip.available_range(): {clip.available_range()}")
            # _logger.debug(f"  clip.available_range().duration: {clip.available_range().duration}")
            # _logger.debug(
            #     f"  clip.available_range().rescaled_to(25): {(clip.available_range().end_time_inclusive()).rescaled_to(25)}"
            # )
            # _logger.debug(
            #     f"  clip.available_range().value_rescaled_to(25): {clip.available_range().end_time_exclusive().value_rescaled_to(25)}"
            # )

            offsetEnd = (
                start
                + clip.available_range().end_time_exclusive().value_rescaled_to(25)
                - opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_exclusive())
                - opentimelineio.opentime.to_frames(clip.source_range.start_time)
            )

            frameStart = ow.get_clip_frame_start(clip, fps)
            frameEnd = ow.get_clip_frame_end(clip, fps)
            frameFinalStart = ow.get_clip_frame_final_start(clip, fps)
            frameFinalEnd = ow.get_clip_frame_final_end(clip, fps)
            frameOffsetStart = ow.get_clip_frame_offset_start(clip, fps)
            frameOffsetEnd = ow.get_clip_frame_offset_end(clip, fps)
            frameDuration = ow.get_clip_frame_duration(clip, fps)
            frameFinalDuration = ow.get_clip_frame_final_duration(clip, fps)

            frameStart += offsetFrameNumber
            frameEnd += offsetFrameNumber
            frameFinalStart += offsetFrameNumber
            frameFinalEnd += offsetFrameNumber

            _logger.debug(
                f"Abs clip values: clip frameStart: {frameStart}, frameFinalStart:{frameFinalStart}, frameFinalEnd:{frameFinalEnd}, frameEnd: {frameEnd}"
            )
            _logger.debug(
                f"Rel clip values: clip frameOffsetStart: {frameOffsetStart}, frameOffsetEnd:{frameOffsetEnd}"
            )
            _logger.debug(
                f"Duration clip values: clip frameDuration: {frameDuration}, frameFinalDuration:{frameFinalDuration}"
            )

            vse_render = bpy.context.window_manager.UAS_vse_render
            newClipInVSE = vse_render.createNewClip(
                bpy.context.scene,
                media_path,
                trackInd,
                frameStart,
                offsetStart=frameOffsetStart,
                offsetEnd=frameOffsetEnd,
                importVideo=track_type == "VIDEO",
                importAudio=track_type == "AUDIO",
                clipName=clip.name,
            )

            if newClipInVSE is not None:

                clipEnabled = True
                if verbose:
                    print(f" -*- clip metadata: {clip.metadata}")

                if "fcp_xml" in clip.metadata:
                    # print(" -*- fcp_xml is ok")
                    # print(f"metadata; clip.metadata['fcp_xml']['enabled']: {clip.metadata['fcp_xml']['enabled']}")
                    if "enabled" in clip.metadata["fcp_xml"]:
                        clipEnabled = not ("FALSE" == clip.metadata["fcp_xml"]["enabled"])
                newClipInVSE.mute = not clipEnabled

                if track_type == "AUDIO":
                    if "fcp_xml" in clip.metadata:
                        if "filter" in clip.metadata["fcp_xml"]:
                            if "effect" in clip.metadata["fcp_xml"]["filter"]:
                                if "parameter" in clip.metadata["fcp_xml"]["filter"]["effect"]:
                                    if "parameter" in clip.metadata["fcp_xml"]["filter"]["effect"]:
                                        if "value" in clip.metadata["fcp_xml"]["filter"]["effect"]["parameter"]:
                                            volumeVal = float(
                                                clip.metadata["fcp_xml"]["filter"]["effect"]["parameter"]["value"]
                                            )
                                            if verbose:
                                                print(f" volume value: {volumeVal}")
                                            newClipInVSE.volume = volumeVal

                    audio_volume_keyframes = []
                    if clip.metadata is not None:
                        effect = clip.metadata.get("fcp_xml", {}).get("filter", {}).get("effect")
                        if effect is not None and effect["effectcategory"] == "audiolevels":
                            keyframe_data = effect.get("parameter", {}).get("keyframe")
                            if keyframe_data is not None:
                                if isinstance(keyframe_data, opentimelineio._otio.AnyVector):
                                    for keyframe in keyframe_data:
                                        frame = opentimelineio.opentime.to_frames(
                                            opentimelineio.opentime.RationalTime(float(keyframe["when"]))
                                        )
                                        audio_volume_keyframes.append((frame, float(keyframe["value"])))
                                else:
                                    frame = opentimelineio.opentime.to_frames(
                                        opentimelineio.opentime.RationalTime(float(keyframe_data["when"]))
                                    )
                                    audio_volume_keyframes.append((frame, float(keyframe_data["value"])))

                    for f, v in audio_volume_keyframes:
                        newClipInVSE.volume = v
                        newClipInVSE.keyframe_insert("volume", frame=f)

            if verbose:
                vse_render.printClipInfo(newClipInVSE, printTimeInfo=True)
            # _logger.debug(f"newClipInVSE: {newClipInVSE.name}")

            # frameStart = newClipInVSE.frame_start
            # frameEnd = -1  # newClipInVSE.frame_end
            # frameFinalStart = newClipInVSE.frame_final_start
            # frameFinalEnd = newClipInVSE.frame_final_end
            # frameOffsetStart = newClipInVSE.frame_offset_start
            # frameOffsetEnd = newClipInVSE.frame_offset_end
            # frameDuration = newClipInVSE.frame_duration
            # frameFinalDuration = newClipInVSE.frame_final_duration

            # frameStart += offsetFrameNumber
            # frameEnd += offsetFrameNumber
            # frameFinalStart += offsetFrameNumber
            # frameFinalEnd += offsetFrameNumber

            # _logger.debug(
            #     f"Abs clip values: clip frameStart: {frameStart}, frameFinalStart:{frameFinalStart}, frameFinalEnd:{frameFinalEnd}, frameEnd: {frameEnd}"
            # )
            # _logger.debug(
            #     f"Rel clip values: clip frameOffsetStart: {frameOffsetStart}, frameOffsetEnd:{frameOffsetEnd}"
            # )
            # _logger.debug(
            #     f"Duration clip values: clip frameDuration: {frameDuration}, frameFinalDuration:{frameFinalDuration}"
            # )

            # fix to prevent the fact that the sound is sometimes longer than expected by 1 frame
            if newClipInVSE.frame_final_duration > ow.get_clip_frame_final_duration(clip, fps):
                if verbose:
                    print(
                        f"newClipInVSE.frame_final_duration: {newClipInVSE.frame_final_duration}, ow.get_clip_frame_final_duration(clip, fps): {ow.get_clip_frame_final_duration(clip, fps)}"
                    )
                # newClipInVSE.frame_offset_end = -1 * (
                #     newClipInVSE.frame_final_duration - ow.get_clip_frame_final_duration(clip, fps)
                # )
                newClipInVSE.frame_final_duration = ow.get_clip_frame_final_duration(clip, fps)

            # bpy.context.window_manager.UAS_vse_render.createNewClip(
            #     bpy.context.scene,
            #     media_path,
            #     trackInd,
            #     start - otio_clipLocalCutStart,
            #     offsetStart=otio_clipLocalCutStart,
            #     offsetEnd=offsetEnd,
            #     # offsetEnd=end - otio_clipLocalCutStart + trimmedClipDuration,
            #     # trimmedClipDuration=trimmedClipDuration,
            #     importVideo=track_type == "VIDEO",
            #     importAudio=track_type == "AUDIO",
            # )

    pass


def importToVSE(
    timeline,
    vse,
    timeRange=None,
    offsetFrameNumber=0,
    track_type="ALL",
    videoTracksList=None,
    audioTracksList=None,
    alternative_media_folder="",
):
    """
        track_type can be "ALL", "VIDEO" or "AUDIO"
    """
    # print(f"\nimportToVSE: track_type: {track_type}")

    # alternative_media_folder = Path(otioFile).parent

    # bpy.context.scene.frame_start = -999999
    # bpy.context.scene.frame_end = 999999

    # video
    if "ALL" == track_type or "VIDEO" == track_type:
        for trackInd, editTrack in enumerate(timeline.video_tracks()):
            if videoTracksList is None or (trackInd + 1) in videoTracksList:
                importTrack(
                    editTrack,
                    trackInd + 1,
                    "VIDEO",
                    timeRange=timeRange,
                    offsetFrameNumber=offsetFrameNumber,
                    alternative_media_folder=alternative_media_folder,
                )

    # audio
    if "ALL" == track_type or "AUDIO" == track_type:
        for trackInd, editTrack in enumerate(timeline.audio_tracks()):
            if audioTracksList is None or (trackInd + 1) in audioTracksList:
                importTrack(
                    editTrack,
                    trackInd + 1,
                    "AUDIO",
                    timeRange=timeRange,
                    offsetFrameNumber=offsetFrameNumber,
                    alternative_media_folder=alternative_media_folder,
                )


def getSequenceListFromOtio(otioFile):

    timeline = opentimelineio.adapters.read_from_file(otioFile)
    return getSequenceListFromOtioTimeline(timeline)


def getSequenceNameFromMediaName(fileName):
    print("\n\n **** Deprecated : imports.py getSequenceNameFromMediaName !!!")
    seqName = ""

    seq_pattern = "Seq"
    media_name_splited = fileName.split("_")
    if 2 <= len(media_name_splited):
        seqName = media_name_splited[1]

    return seqName

    # get file names only
    file_list = list()
    for item in media_list:
        filename = os.path.split(item)[1]
        file_list.append(os.path.splitext(filename)[0])
        # print(item)

    # get sequences
    seq_list = list()
    seq_pattern = "_seq"
    for item in file_list:
        if seq_pattern in item.lower():
            itemSplited = item.split("_")
            if 2 <= len(itemSplited):
                if itemSplited[1] not in seq_list:
                    seq_list.append(itemSplited[1])

    # for item in seq_list:
    #     print(item)

    return seq_list


def getSequenceListFromOtioTimeline(timeline):

    print("\n\n **** Deprecated : imports.py getSequenceListFromOtioTimeline !!!")
    if timeline is None:
        _logger.error("getSequenceListFromOtioTimeline: Timeline is None!")
        return

    media_list = ow.get_media_list(timeline, track_type="VIDEO")

    # get file names only
    file_list = list()
    for item in media_list:
        filename = os.path.split(item)[1]
        file_list.append(os.path.splitext(filename)[0])
        # print(item)

    # get sequences
    seq_list = list()
    seq_pattern = "_seq"
    for item in file_list:
        if seq_pattern in item.lower():
            itemSplited = item.split("_")
            if 2 <= len(itemSplited):
                if itemSplited[1] not in seq_list:
                    seq_list.append(itemSplited[1])

    # for item in seq_list:
    #     print(item)

    return seq_list


def importAnimatic(montageOtio, sequenceName, animaticFile, offsetFrameNumber=0):
    if not Path(animaticFile).exists():
        return

    vse_render = bpy.context.window_manager.UAS_vse_render
    # newClipInVSE = vse_render.createNewClip(
    #     bpy.context.scene,
    #     animaticFile,
    #     31,
    #     25,
    #     # offsetStart=frameOffsetStart,
    #     # offsetEnd=frameOffsetEnd,
    #     importVideo=True,
    #     importAudio=True,
    #     clipName="Animatic",
    # )

    # sequence
    # seq = montageOtio.get_sequence_by_name(sequenceName)
    # if seq is not None:

    #     offsetFrameNumber = 25
    #     newClipInVSE = vse_render.createNewClipFromRange(
    #         bpy.context.scene,
    #         animaticFile,
    #         31,
    #         frame_start=offsetFrameNumber - 1 * seq.get_frame_start(),
    #         frame_final_start=1 * offsetFrameNumber,
    #         frame_final_end=seq.get_frame_duration() + offsetFrameNumber,
    #         importVideo=True,
    #         importAudio=True,
    #         clipName="Animatic",
    #     )
    #     if newClipInVSE is not None:
    #         pass
    # pass

    seq = montageOtio.get_sequence_by_name(sequenceName)
    if seq is not None:
        shots = seq.getEditShots()

        offsetFrameNumber = 0
        for sh in shots:
            print(f"{sh.get_name()}: sh.get_frame_final_start(): {sh.get_frame_final_start()}")

            #####
            # Code has to be repeated otherwise not working... :/
            #####
            newClipInVSE = vse_render.createNewClipFromRange(
                bpy.context.scene,
                animaticFile,
                31,
                frame_start=0,  # - 1 * sh.get_frame_start(),
                frame_final_start=1 * offsetFrameNumber + sh.get_frame_final_start(),
                frame_final_end=sh.get_frame_final_end() + offsetFrameNumber,
                importVideo=True,
                importAudio=False,
                clipName="Animatic",
            )
            print(f"newClipInVSE video .frame_start: {newClipInVSE.frame_start}")

            newClipInVSE = vse_render.createNewClipFromRange(
                bpy.context.scene,
                animaticFile,
                32,
                frame_start=0,  # - 1 * sh.get_frame_start(),
                frame_final_start=1 * offsetFrameNumber + sh.get_frame_final_start(),
                frame_final_end=sh.get_frame_final_end() + offsetFrameNumber,
                importVideo=False,
                importAudio=True,
                clipName="Animatic",
            )

            print(f"newClipInVSE audio.frame_start: {newClipInVSE.frame_start}")


def importOtioToVSE(otioFile, vse, importAtFrame=0, importVideoTracks=True, importAudioTracks=True):
    print("ImportOtioToVSE: **** Deprecated ****")

    # def importTrack(track, trackInd, importAtFrame):
    #     for i, clip in enumerate(track.each_clip()):
    #         clipName = clip.name
    #         print("   Clip name: ", clipName)
    #         print("   Clip ind: ", i)

    #         print("Import Otio clip.media_reference.target_url: ", clip.media_reference.target_url)
    #         media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
    #         print("Import Otio media_path: ", media_path)
    #         print("  Import at frame: ", importAtFrame)
    #         if not media_path.exists():
    #             # Lets find it inside next to the xml
    #             media_path = Path(otioFile).parent.joinpath(media_path.name)
    #             print("** not found, so Path(self.otioFile).parent: ", Path(otioFile).parent)
    #             print("   and new media_path: ", media_path)

    #         if media_path.exists():
    #             media_path = str(media_path)

    #             # local clip infos:

    #             _logger.info(f"Logger info")
    #             _logger.warning(f"logger warning")
    #             _logger.error(f"logger error")

    #             start = opentimelineio.opentime.to_frames(clip.range_in_parent().start_time) + importAtFrame
    #             end = opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + importAtFrame
    #             duration = opentimelineio.opentime.to_frames(clip.available_range().end_time_inclusive())

    #             # local clip infos:
    #             otio_clipSourceRange = clip.source_range
    #             # clip cut in in local clip time ref (= relatively to clip start)
    #             otio_clipLocalCutStart = opentimelineio.opentime.to_frames(clip.source_range.start_time)
    #             # clip cut out in local clip time ref (= relatively to clip start)
    #             otio_clipLocalCutEnd = None  # opentimelineio.opentime.to_frames(clip.source_range.end_time())
    #             otio_clipLocalCutEndInclus = opentimelineio.opentime.to_frames(clip.source_range.end_time_inclusive())
    #             print(
    #                 f"\n   otio_clipSourceRange: {otio_clipSourceRange}, otio_clipLocalCutStart: {otio_clipLocalCutStart}, otio_clipLocalCutEnd: {otio_clipLocalCutEnd}, otio_clipLocalCutEndInclus: {otio_clipLocalCutEndInclus}"
    #             )

    #             otio_clipLocalCutEndInclus = opentimelineio.opentime.to_frames(clip.source_range.end_time_inclusive())
    #             trimmedClipDuration = opentimelineio.opentime.to_frames(clip.duration())
    #             print(
    #                 f"   start: {start}, end: {end}, duration: {duration}, trimmedClipDuration: {trimmedClipDuration}, otio_clipSourceRange: {otio_clipSourceRange}, otio_clipLocalCutEndInclus: {otio_clipLocalCutEndInclus}"
    #             )
    #             print("otio_clipSourceRange[0][0]: ", otio_clipSourceRange.start_time)
    #             print(
    #                 "otio_clipSourceRange[0][0]: ", opentimelineio.opentime.to_frames(otio_clipSourceRange.start_time)
    #             )
    #             # print(f"   range_from_start_end_time: {clip.range_in_parent().range_from_start_end_time()}")
    #             bpy.context.window_manager.UAS_vse_render.createNewClip(
    #                 bpy.context.scene,
    #                 media_path,
    #                 trackInd,
    #                 start - otio_clipLocalCutStart,
    #                 offsetStart=otio_clipLocalCutStart,
    #                 trimmedClipDuration=trimmedClipDuration,
    #             )

    #     pass

    #        try:
    timeline = opentimelineio.adapters.read_from_file(otioFile)
    # if len(timeline.video_tracks()):
    #     track = timeline.video_tracks()[0]  # Assume the first one contains the shots.

    # video
    if importVideoTracks:
        for trackInd, editTrack in enumerate(timeline.video_tracks()):
            print(f"\nDeprec Channel Name: {editTrack.name}, {trackInd}")
        #   importTrack(editTrack, trackInd + 1, importAtFrame)

    # audio
    if importAudioTracks:
        for trackInd, editTrack in enumerate(timeline.audio_tracks()):
            print(f"\nDeprec Channel Name: {editTrack.name}, {trackInd}")
        #  importTrack(editTrack, trackInd + 1, importAtFrame)


def import_otio(scene, filepath, old_dir, new_dir):
    old_dir = old_dir.replace("\\", "/")
    new_dir = new_dir.replace("\\", "/")
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    seq_editor = scene.sequence_editor

    timeline = opentimelineio.adapters.read_from_file(filepath)
    bad_file_uri_check = re.compile(
        r"^/\S:.*"
    )  # file uri parsing on windows can result in a leading / in front of the drive letter.

    for i, track in enumerate(timeline.tracks):
        track_kind = track.kind

        for clip in track.each_clip():
            media_path = unquote_plus(urlparse(clip.media_reference.target_url).path).replace("\\", "//")

            head, tail = os.path.split(media_path)
            media_path = new_dir + tail
            print("media_path: ", media_path)

            # if bad_file_uri_check.match(media_path):  # Remove leading /
            #     media_path = media_path[1:]
            # media_path = media_path.replace(old_dir, new_dir)

            # print("media_path: ", media_path)
            # media_path = Path(media_path)
            if not Path(media_path).exists():
                print(f"Could not be find {media_path}.")
            #     continue

            # if track_kind == "Video":
            #     c = seq_editor.sequences.new_movie(
            #         clip.name, str(media_path), i, opentimelineio.opentime.to_frames(clip.range_in_parent().start_time)
            #     )
            #     c.frame_final_duration = opentimelineio.opentime.to_frames(clip.duration())

            elif track_kind == "Audio":
                c = seq_editor.sequences.new_sound(
                    clip.name, str(media_path), i, opentimelineio.opentime.to_frames(clip.range_in_parent().start_time)
                )
                c.frame_final_duration = opentimelineio.opentime.to_frames(clip.duration())

