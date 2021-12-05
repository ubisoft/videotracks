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
OTIO
"""


from videotracks.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def register():
    from . import operators

    try:
        import opentimelineio as otio

        otioVersion = otio.__version__
        otioVersionStr = f" - OpenTimelineIO V. {otioVersion}"
    except Exception:
        otioVersionStr = " - OpenTimelineIO not available"

    _logger.debug_ext("       - Registering OTIO Package" + otioVersionStr, form="REG")

    operators.register()


def unregister():
    from . import operators

    _logger.debug_ext("       - Unregistering OTIO Package", form="UNREG")

    operators.unregister()
