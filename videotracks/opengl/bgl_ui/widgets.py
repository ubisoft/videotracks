# -*- coding: utf-8 -*-

from enum import Enum, auto

import bpy, bgl
from typing import Callable, Union, Tuple, Any, List

from .types import BGLBound, BGLColor, BGLCoord, BGLRegion, BGLPropValue, BGLProp
from .geometry import *
from . import utils

#
# Reflexions
#
#  Callback object?
#  What callback you get as argument ? self ?

def _nop(*args, **kwargs):
    pass


class BGLWidget:
    position = BGLProp(BGLCoord())
    visible = BGLProp(True)

    def __init__(self, **prop_values):
        for k, v in prop_values.items():
            setattr(self, k, v)

        self.debug = True

    def get_bound(self, region: BGLRegion):
        return BGLBound()

    def _draw(self, region: BGLRegion):
        if region.bound.do_overlap(self.get_bound(region)):
            self.draw(region)

    def draw(self, region: BGLRegion):
        pass

    def _handle_event(self, region: BGLRegion, event: bpy.types.Event) -> bool:
        if region.bound.do_overlap(self.get_bound(region)):
            return self.handle_event(region, event)

        return False

    def handle_event(self, region: BGLRegion, event: bpy.types.Event) -> bool:
        return False

    def debug_print(self, *args, **kwargs):
        if self.debug is True:
            print(*args, **kwargs)


class BGLLabel(BGLWidget):
    """
        text_aligment can be: TOP_LEFT, TOP_MID, TOP_RIGHT, MID_RIGHT, BOTTOM_RIGHT, BOTTOM_MID, BOTTOM_LEFT, MID_LEFT, CENTER
    """

    width = BGLProp(100)
    height = BGLProp(100)
    bgColor = BGLProp(BGLColor(0.2, 0.2, 0.8, 1.0))

    text = BGLProp("Label")
    text_size = BGLProp(11)
    text_color = BGLProp(BGLColor(0.9, 0.9, 0.9))

    rotation = BGLProp(0)
    # wkip to finish
    text_alignment = "CENTER"

    def __init__(self, **prop_values):
        BGLWidget.__init__(self, **prop_values)

        self._geometry = BGLRect(width=lambda: self.width, height=lambda: self.height)
        self._geometry.color = lambda: self.bgColor
        self._geometry.position = lambda: self.position

        self._text_geometry = BGLText(
            text=lambda: self.text, centered=False, color=self.text_color, size=self.text_size
        )

        # for text with rotation:
        # self._text_geometry.position = lambda: self._geometry.get_bound().mid_right

        self._text_geometry.position = lambda: self._geometry.get_bound().get_point(self.text_alignment)

        # icon_size = min ( height, width )
        # self._icon_geometry = BGLTexture ( 50, 1 )
        # self._icon_geometry.image = lambda: self.icon
        # self._icon_geometry.position = lambda: self._geometry.position #+ BGLCoord ( 0, icon_size *.5 )

    def get_bound(self, region):
        return self._geometry.get_bound(region)

    def draw(self, region):
        self._geometry.draw(region)
        self._text_geometry.drawAdv(region, rotation=self.rotation)


class BGLButton(BGLWidget):
    width = BGLProp(50)
    height = BGLProp(100)
    color = BGLProp(BGLColor(0.2, 0.2, 0.2))
    highlight_color = BGLProp(BGLColor(1, 1, 1))

    border_width = 0
    border_color = BGLProp(BGLColor(0.2, 0.2, 0.2))

    text = BGLProp("Button")
    text_size = BGLProp(11)
    text_color = BGLProp(BGLColor(0.9, 0.9, 0.9))

    icon = BGLProp(None)  # BGLImage

    def __init__(self, **prop_values):
        BGLWidget.__init__(self, **prop_values)

        self.highlight_color = lambda s=self: s.color ** 0.8
        self.is_highlighted = False

        if self.border_width:
            self._border_geometry = BGLRectLine(
                width=lambda: self.width, height=lambda: self.height, line_width=lambda: self.border_width
            )
            self._border_geometry.color = lambda: self.border_color
            self._border_geometry.position = lambda: self.position

        self._geometry = BGLRect(width=lambda: self.width, height=lambda: self.height)
        self._geometry.color = lambda: self.highlight_color if self.is_highlighted else self.color
        self._geometry.position = lambda: self.position

        self._text_geometry = BGLText(text=lambda: self.text, centered=True, color=self.text_color, size=self.text_size)
        self._text_geometry.position = lambda: self._geometry.get_bound().center

        # icon_size = min ( height, width )
        # self._icon_geometry = BGLTexture ( 50, 1 )
        # self._icon_geometry.image = lambda: self.icon
        # self._icon_geometry.position = lambda: self._geometry.position #+ BGLCoord ( 0, icon_size *.5 )

        self._on_clicked_callback = _nop
        self._on_highlighted_callback = _nop
        self._is_pushed = False

    @property
    def clicked_callback(self):
        return self._on_clicked_callback

    @clicked_callback.setter
    def clicked_callback(self, callback: Callable[[], None]):
        if callback is None:
            self._on_clicked_callback = _nop
        else:
            self._on_clicked_callback = callback

    @property
    def highlighted_callback(self):
        return self._on_highlighted_callback

    @highlighted_callback.setter
    def highlighted_callback(self, callback: Callable[[], None]):
        if callback is None:
            self._on_highlighted_callback = _nop
        else:
            self._on_highlighted_callback = callback

    def get_bound(self, region):
        return self._geometry.get_bound(region)

    def handle_event(self, region, event: bpy.types.Event) -> bool:
        mouse_pos = region.mouse_to_region(BGLCoord(event.mouse_x, event.mouse_y))
        if event.type == "LEFTMOUSE":
            if self._geometry.is_over(mouse_pos, region):
                if event.value == "PRESS":
                    self._is_pushed = True
                elif event.value == "RELEASE":
                    if self._is_pushed:
                        self._on_clicked_callback()
                        return True
                    self._is_pushed = False

        elif event.type == "MOUSEMOVE":
            if self._geometry.is_over(mouse_pos, region):
                self.is_highlighted = True
                self._on_highlighted_callback ()
            else:
                self.is_highlighted = False
                self._on_highlighted_callback()

        return False

    def draw(self, region):
        if self.border_width:
            self._border_geometry.draw(region)
        self._geometry.draw(region)
        # self._icon_geometry.draw ( region )
        self._text_geometry.draw(region)


class BGLGeometryStamp(BGLWidget):
    geometry = BGLProp(None)
    color = BGLProp(BGLColor())

    def __init__(self, **prop_values):  # Currently no position since the geometry have one as well.
        BGLWidget.__init__(self, **prop_values)
        self.geometry.position = lambda self=self: self.position

    def get_bound(self, region):
        return self.geometry.get_bound(region)

    def draw(self, region: BGLRegion):
        self.geometry.draw(region)


class BGLCheckBox(BGLWidget):
    checked = BGLProp(False)
    text = BGLProp("")
    size = BGLProp(18)
    color = BGLProp(BGLColor(0.0, 0.4, 1))

    def __init__(self, **prop_values):
        BGLWidget.__init__(self, **prop_values)
        self._text_geo = BGLText(text=lambda: self.text)

        self._bg_rect = BGLRect(width=lambda: self.size, height=lambda: self.size, color=BGLColor(0.01, 0.01, 0.01))
        self._fg_rect = BGLRect(
            width=lambda: self.size - 2,
            height=lambda: self.size - 2,
            color=lambda: self.color ** 0.1 if self._highlighted else self.color,
        )

        self._bg_rect.position = lambda: self.position
        self._fg_rect.position = lambda: self.position + BGLCoord(1, 1)

        self._text_geo.position = lambda: self.position + BGLCoord(self.size + 4, self._text_geo.height * 0.5)

        self._highlighted = False
        self._is_pushed = False

        self._on_clicked_callback = _nop

    @property
    def clicked_callback(self):
        return self._on_clicked_callback

    @clicked_callback.setter
    def clicked_callback(self, callback: Callable[[bool], None]):
        if callback is None:

            def update_check(s):
                self.checked = s

            self._on_clicked_callback = update_check
        else:
            self._on_clicked_callback = callback

    def get_bound(self, region: BGLRegion):
        return self._bg_rect.get_bound(region) + self._text_geo.get_bound(region)

    def handle_event(self, region, event: bpy.types.Event) -> bool:
        mouse_pos = region.mouse_to_region(BGLCoord(event.mouse_x, event.mouse_y))
        if event.type == "LEFTMOUSE":
            if self._bg_rect.is_over(mouse_pos, region):
                if event.value == "PRESS":
                    self._is_pushed = True
                elif event.value == "RELEASE":
                    if self._is_pushed:
                        self._on_clicked_callback(not self.checked)
                        return True
                    self._is_pushed = False

        elif event.type == "MOUSEMOVE":
            if self._bg_rect.is_over(mouse_pos, region):
                self._highlighted = True
            else:
                self._highlighted = False

        return False

    def draw(self, region: BGLRegion):
        self._bg_rect.draw(region)
        if self.checked:
            self._fg_rect.draw(region)
        self._text_geo.draw(region)


class BGLSlider(BGLWidget):
    width = BGLProp(10)
    height = BGLProp(4)
    min = BGLProp(0)
    max = BGLProp(100)
    value = BGLProp(50)
    back_color = BGLProp(BGLColor(0.01, 0.01, 0.01))
    front_color = BGLProp(BGLColor(0.9, 0.9, 0.9))

    def __init__(self, **prop_values):
        BGLWidget.__init__(self, **prop_values)
        self.on_value_changed: Callable[[Any], None] = None

        self._back_geo = BGLRect(width=lambda: self.width, height=lambda: self.height)
        self._back_geo.position = lambda: self.position
        self._front_geo = BGLRect(width=lambda: self.width * 0.5, height=lambda: self.height)
        self._front_geo.position = lambda: self.position
        self._back_geo.color = lambda: self.back_color
        self._front_geo.color = lambda: self.front_color
        self._focused = False

    def _update_value_mouse_interaction(self, mouse_pos, region):
        """
        Update geometry and sets the value.
        """
        bound = self._back_geo.get_bound(region)
        val = utils.remap(mouse_pos.x, bound.min.x, bound.max.x, self.min, self.max)
        if self.on_value_changed is None:
            self.value = val
        else:
            self.on_value_changed(val)

    def handle_event(self, region, event: bpy.types.Event) -> bool:

        mouse_pos = region.mouse_to_region(BGLCoord(event.mouse_x, event.mouse_y))
        res = False
        if event.type == "LEFTMOUSE":
            if self._back_geo.is_over(mouse_pos, region):
                if event.value == "PRESS":
                    self._update_value_mouse_interaction(mouse_pos, region)
                    res = True
                    self._focused = True
                elif event.value == "RELEASE":
                    self._update_value_mouse_interaction(mouse_pos, region)
                    res = True
                    self._focused = False
            else:
                self._focused = False

        elif event.type == "MOUSEMOVE":
            if self._focused:
                if event.value == "PRESS":
                    self._update_value_mouse_interaction(mouse_pos, region)
                    res = True
            elif event.value == "RELEASE":
                self._focused = False

        return res

    def get_bound(self, region):
        return self._back_geo.get_bound(region)

    def draw(self, region: BGLRegion):
        self._front_geo.width = utils.remap(self.value, self.min, self.max, 0, 1) * self._back_geo.width

        self._back_geo.draw(region)
        self._front_geo.draw(region)


# ---------------- LAYOUT WIDGETS ------------------#


class BGLLayoutBase(BGLWidget):
    def __init__(self, **prop_values):
        BGLWidget.__init__(self, **prop_values)
        self._widgets: List[BGLWidget] = list()

    def add_widget(self, widget):
        self._widgets.append(widget)

    def layout_widgets(self, region):
        raise NotImplementedError()

    def handle_event(self, region, event: bpy.types.Event):
        self.layout_widgets(region)
        for wdgt in self._widgets:
            wdgt.handle_event(region, event)

    def draw(self, region):
        self.layout_widgets(region)
        for wdgt in self._widgets:
            wdgt.draw(region)

    def get_bound(self, region: BGLRegion):
        if self._widgets:
            bound = self._widgets[0].get_bound(region)
            self.layout_widgets(region)
            for wgdt in self._widgets[1:]:
                bound += wgdt.get_bound(region)
        else:
            bound = BGLBound()

        return bound


class BGLLayoutH(BGLLayoutBase):
    spacing = BGLProp(5)
    fill_region = BGLProp(False)

    def layout_widgets(self, region):
        pos = BGLCoord(*self.position)

        spacing = self.spacing
        if self.fill_region:
            total_widgets_width = 0
            pos.x = region.bound.min.x
            for wdgt in self._widgets:
                total_widgets_width += wdgt.get_bound(region).width
            free_space = region.bound.width - total_widgets_width
            spacing = max(free_space / max(1, (len(self._widgets) - 1)), self.spacing)

        for wdgt in self._widgets:
            wdgt.position = BGLCoord(*pos)
            pos.x += wdgt.get_bound(region).width + spacing


class BGLLayoutV(BGLLayoutBase):
    spacing = BGLProp(5)
    fill_region = BGLProp(False)

    def layout_widgets(self, region):
        pos = BGLCoord(*self.position)
        spacing = self.spacing
        if self.fill_region:
            pos.y = region.bound.min.y
            total_widgets_height = 0
            for wdgt in self._widgets:
                total_widgets_height += wdgt.get_bound(region).height
            free_space = region.bound.height - total_widgets_height
            spacing = max(free_space / max(1, (len(self._widgets) - 1)), self.spacing)

        for wdgt in self._widgets:
            wdgt.position = BGLCoord(*pos)
            pos.y += wdgt.get_bound(region).height + spacing


class BGLRegionDock(BGLLayoutBase):
    class DockRegion(Enum):
        TOP = auto()
        BOTTOM = auto()
        RIGHT = auto()
        LEFT = auto()

    dock_region = BGLProp(DockRegion.LEFT)
    relative_pos = BGLProp(0.5)

    def layout_widgets(self, region):
        if not self._widgets:
            return

        widgets_height = 0
        widgets_width = 0
        for widget in self._widgets:
            bound = widget.get_bound(region)
            widgets_height += bound.height
            widgets_width += bound.width

        if self.dock_region == self.DockRegion.RIGHT or self.dock_region == self.DockRegion.LEFT:
            # compute initial placement of first widget
            y_offset = utils.clamp(
                utils.remap(self.relative_pos, 0, 1, region.bound.min.y, region.bound.max.y) - widgets_height * 0.5,
                region.bound.min.y,
                region.bound.max.y - widgets_height,
            )
            for widget in self._widgets:
                bound = widget.get_bound(region)
                if self.dock_region == self.DockRegion.LEFT:
                    widget.position.x = region.bound.min.x
                else:
                    widget.position.x = region.bound.max.x - bound.width

                widget.position.y = y_offset
                y_offset += bound.height

        elif self.dock_region == self.DockRegion.TOP or self.dock_region == self.DockRegion.BOTTOM:
            x_offset = utils.clamp(
                utils.remap(self.relative_pos, 0, 1, region.bound.min.x, region.bound.max.x) - widgets_width * 0.5,
                region.bound.min.x,
                region.bound.max.x - widgets_width,
            )

            for widget in self._widgets:
                bound = widget.get_bound(region)
                if self.dock_region == self.DockRegion.BOTTOM:
                    widget.position.y = region.bound.min.y
                else:
                    widget.position.y = region.bound.max.y - bound.height

                widget.position.x = x_offset
                x_offset += bound.width
