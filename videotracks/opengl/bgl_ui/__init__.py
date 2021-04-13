# -*- coding: utf-8 -*-
from typing import Union
import bpy
from .utils import get_region_at_xy
from .widgets import BGLWidget, BGLRegion
from .types import BGLTransform


class BGLCanvas:
    def __init__(self, transform=None, crop_left=0, crop_bottom=0, crop_right=0, crop_top=0):
        BGLWidget.__init__(self)
        self._widgets: list[BGLWidget] = list()
        self._region = BGLRegion(crop_left, crop_bottom, crop_right, crop_top)
        self._region.transform = BGLTransform() if transform is None else transform
        self._last_widget_handled = None

    def addWidget(self, widget: BGLWidget):
        self._widgets.append(widget)

    def clear(self):
        self._widgets.clear()

    def draw(self, region: bpy.types.Region):
        self._region.bl_region = region
        for wdgt in self._widgets:
            if wdgt.visible:
                wdgt._draw(self._region)

    def handle_event(self, region: bpy.types.Region, event: bpy.types.Event) -> bool:
        self._region.bl_region = region
        # First do the last widget which handled something so it has priority.
        if self._last_widget_handled is not None:
            if self._last_widget_handled.handle_event(self._region, event):
                return True

        for wdgt in reversed(self._widgets):  # LAst defined widget have the priority
            if wdgt is self._last_widget_handled:  # Handled first
                continue
            if wdgt._handle_event(self._region, event):
                self._last_widget_handled = wdgt
                return True

        return False


class BGL_UIOperatorBase(bpy.types.Operator):
    bl_idname = "bgl.operator"
    bl_label = "BGL UI Operator"
    bl_options = {"REGISTER", "INTERNAL"}

    def __init__(self):
        self._draw_handle = None
        self._timer = None
        self.context = None

        self._canvas = list()  # type: list[BGLCanvas]
        self._last_handled_canvas = None

    def add_canva(self, canva):
        self._canvas.append(canva)

    def build_ui(self):
        pass

    def space_type(self) -> Union[bpy.types.SpaceDopeSheetEditor, bpy.types.SpaceView3D, bpy.types.SpaceSequenceEditor]:
        raise NotImplementedError()

    def should_draw(self) -> bool:
        return True

    def should_handle_event(self) -> bool:
        return True

    def should_rebuild_ui(self) -> bool:
        return False

    def should_cancel(self) -> bool:
        raise NotImplementedError()

    def modal(self, context, event):
        if self.should_rebuild_ui():
            self._canvas.clear()
            self.build_ui()

        if not self.should_handle_event():
            return {"PASS_THROUGH"}

        for area in context.screen.areas:
            area.tag_redraw()

        region, _ = get_region_at_xy(context, event.mouse_x, event.mouse_y)
        if region is not None:
            if self._last_handled_canvas is not None:
                if self._last_handled_canvas.handle_event(region, event):
                    return {"RUNNING_MODAL"}

            for canva in reversed(
                self._canvas
            ):  # traversal is reversed because last layers are actually drawn on top so we give them mouse priority.
                if canva is self._last_handled_canvas:  # Handled first.
                    continue
                if canva.handle_event(region, event):
                    self._last_handled_canvas = canva
                    return {"RUNNING_MODAL"}

        if self.should_cancel():
            context.window_manager.event_timer_remove(self._timer)
            self.space_type().draw_handler_remove(self._draw_handle, "WINDOW")

            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def draw(self, context):
        # wkip pour effacer message
        try:
            if self.should_draw():
                for canva in self._canvas:
                    canva.draw(context.region)
        except Exception:
            pass

    def invoke(self, context, event):
        self.context = context

        self._draw_handle = self.space_type().draw_handler_add(self.draw, (context,), "WINDOW", "POST_PIXEL")
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        self.build_ui()

        return {"RUNNING_MODAL"}

