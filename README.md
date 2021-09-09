![](doc/images/Logo_90_A.png)
# Video Tracks - Blender Add-on
Video Tracks is a Blender add-on that provides track headers to the channels of the VSE.

* **Latest <u>GitHub</u> release:** [github.com/ubisoft/videotracks/releases/latest](https://github.com/ubisoft/videotracks/releases/latest)

**Disclaimer**
>**This tool is currently supported for LTS version of Blender 2.83 and up to Blender 2.92**
>
>**At the moment it is NOT compatible with Blender version 2.93 because there is currently no OpenTimelineIO package for Python 3.9**
>
>It was initialy developed for an animated TV series production in 2020 on Blender 2.83. It has the features that were needed at the time but it
may not be considered as feature complete for a more generic purpose. In spite of all our efforts to make it reliable some troubles may occur in use cases we have not faced.
>
<br />

Note that development is on Windows 10. Please report issues and submit PRs for other OSs.


## Purpose

Video Tracks improves the manipulation of the strip channels in the Video Sequence Editor.
It provides a more conventional UI for these channels, making them look and - as much as possible - feel
like video and audio tracks existing in classic editing software. Each channel then gets a "header", an area where it receives
a name and where its content can be globaly controlled.
This is very convenient for previz and 3D layout.

<br />
<img src="docs/img/VideoTracks_screen.png" alt="Video Tracks screenshot" width="70%"/>
<br /><br />


## Installation:
Video Tracks can be installed as any standard Blender add-on. Nevertheless:

>The addon must be installed in Administrator mode so that the OpenTimelineIO Python wheel can
>be downloaded and deployed correctly. Also be sure that your firewall doesn't block the download (or use OpenVPN or equivalent).

Launch Blender, open the Preferences panel and go to the Add-ons section. Press the Install button located at the top of the panel. A dialog box opens, pick the Video Tracks zip file you previously downloaded and validate. The add-on will be installed. Click on the checkbox at the left side of its name to enable it.
Once the addon is enabled, a Video Tracks tab is displayed in the VSE N-Panel.

Now close Blender to save your user preferences with the Video Tracks installation.


## Features

- Several type of tracks are available: Audio, Video, Mixed... Some of them are experimental.
<br />

**Tools:**

- Markers Navigation Bar: A set of buttons allowing fast and easy navigation between markers
- Time Control Bar: Better control on scene time range as well as on VSE zoom range

# History
[Change Log](./CHANGELOG.md)
