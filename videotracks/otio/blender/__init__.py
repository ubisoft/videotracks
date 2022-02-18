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
OTIO files dedicated to Blender
"""


def register():
    print("totototo")
    from . import otio_operators

    otio_operators.register()

    # from . import otio_operators_rss

    # otio_operators_rss.register()


def unregister():
    from . import otio_operators

    otio_operators.unregister()

    # from . import otio_operators_rss

    # otio_operators_rss.unregister()
