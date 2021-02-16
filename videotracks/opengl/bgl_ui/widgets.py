# -*- coding: utf-8 -*-
import bpy, bgl
from typing import Callable, Union, Tuple, Any, List

from .types import BGLBound, BGLColor, BGLCoord, BGLRegion, BGLPropValue, BGLProp
from.geometry import *
from . import shaders
from . import utils


def _nop ( *args, **kwargs ):
    pass


class BGLWidget:
    position = BGLProp ( BGLCoord ( ) )
    visible = BGLProp ( True )

    def __init__ ( self ):
        self.debug = True

    def get_bound ( self, region: BGLRegion ):
        return BGLBound ( )

    def _draw ( self, region: BGLRegion ):
        if region.bound.do_overlap ( self.get_bound ( region ) ):
            self.draw ( region )

    def draw ( self, region: BGLRegion ):
        pass

    def _handle_event ( self, region: BGLRegion, event : bpy.types.Event ) -> bool:
        if region.bound.do_overlap ( self.get_bound ( region ) ):
            return self.handle_event ( region, event )

        return False

    def handle_event ( self, region: BGLRegion, event : bpy.types.Event ) -> bool:
        return False

    def debug_print ( self, *args, **kwargs ):
        if self.debug is True:
            print ( *args, **kwargs )



class BGLButton ( BGLWidget ):
    color = BGLProp ( BGLColor ( .5, .5, .5 )  )
    highlight_color = BGLProp ( BGLColor ( 1, 1, 1 )  )
    text = BGLProp ( "Button" )

    def __init__( self, position: BGLCoord, width, height, text = "Button" ):
        BGLWidget.__init__ ( self )
        self.position = position
        self._width = width
        self._height = height

        self.highlight_color = lambda s = self: s.color ** .8
        self._highlighted = False

        self._geometry = BGLRect ( width, height )
        self._geometry.color = lambda: self.highlight_color if self._highlighted else self.color
        self._geometry.position = lambda: self.position
        self._text_geometry = BGLText ( text = text, center_text = True )
        self._text_geometry.position = lambda : self._geometry.get_bound ( ).center


        self._on_clicked_callback = _nop

        self._prev_click_time = 0
        self._is_pushed = False

    @property
    def clicked_callback ( self ):
        return self._on_clicked_callback

    @clicked_callback.setter
    def clicked_callback ( self, callback: Callable[ [ "BLButton" ], None ] ):
        if callback is None:
            self._on_clicked_callback = _nop
        else:
            self._on_clicked_callback = callback

    def get_bound( self, region ):
        return self._geometry.get_bound ( region )

    def handle_event( self, region, event : bpy.types.Event) -> bool:
        mouse_pos = region.mouse_to_region ( BGLCoord ( event.mouse_x, event.mouse_y ) )
        if event.type == "LEFTMOUSE":
            if self._geometry.is_over ( mouse_pos, region ):
                if event.value == "PRESS":
                    self._is_pushed = True
                elif event.value == "RELEASE":
                    if self._is_pushed:
                        self._on_clicked_callback ( )
                        return True
                    self._is_pushed = False

        elif event.type == "MOUSEMOVE":
            if self._geometry.is_over ( mouse_pos, region ):
                self._highlighted = True
            else:
                self._highlighted = False

        return False


    def draw ( self, region ):
        self._geometry.draw ( region )
        self._text_geometry.draw ( region )



class BGLGeometryStamp ( BGLWidget ):
    geometry = BGLProp ( None )
    color = BGLProp ( BGLColor ( ) )
    def __init__ ( self, position, geometry ): # Currently no position since the geometry have one as well.
        BGLWidget.__init__ ( self )
        self.position = position
        self.geometry = geometry
        self.geometry.position = lambda self = self: self.position

    def get_bound( self, region ):
        return self.geometry.get_bound ( region )

    def draw ( self, region: BGLRegion ):
        self.geometry.draw ( region )



class BGLSlider ( BGLWidget ):
    min = BGLProp ( 0 )
    max = BGLProp ( 100 )
    value = BGLProp ( 50 )
    back_color = BGLProp ( BGLColor ( .1, .1 , .3 ) )
    front_color = BGLProp ( BGLColor ( .4, .4 , .9 ) )

    def __init__ ( self, position, width, height ):
        BGLWidget.__init__ ( self )
        self.position = position
        self.on_value_changed: Callable[ [ Any ], None ] = None

        self._back_geo = BGLRect ( width, height )
        self._back_geo.position = position
        self._front_geo = BGLRect ( width * .5, height )
        self._front_geo.position = position
        self._back_geo.color = self.back_color
        self._front_geo.color = self.front_color
        self._focused = False


    def _update_value_mouse_interaction ( self, mouse_pos, region ):
        """
        Update geometry and sets the value.
        """
        bound = self._back_geo.get_bound ( region )
        val = utils.remap ( mouse_pos.x, bound.min.x, bound.max.x, self.min, self.max )
        if self.on_value_changed is None:
            self.value = val
        else:
            self.on_value_changed ( val )

    def handle_event( self, region, event : bpy.types.Event) -> bool:

        mouse_pos = region.mouse_to_region ( BGLCoord ( event.mouse_x, event.mouse_y ) )
        res = False
        if event.type == "LEFTMOUSE":
            if self._back_geo.is_over ( mouse_pos, region ):
                if event.value == "PRESS":
                    self._update_value_mouse_interaction ( mouse_pos, region )
                    res = True
                    self._focused = True
                elif event.value == "RELEASE":
                    self._update_value_mouse_interaction ( mouse_pos, region )
                    res = True
                    self._focused = False
            else:
                self._focused = False

        elif event.type == "MOUSEMOVE":
            if self._focused:
                if event.value == "PRESS":
                    self._update_value_mouse_interaction ( mouse_pos, region )
                    res = True
            elif event.value == "RELEASE":
                self._focused = False
        print ( "slider", res)
        return res

    def get_bound( self, region ):
        return self._back_geo.get_bound ( region )

    def draw( self, region: BGLRegion ):
        self._front_geo.width = utils.remap ( self.value, self.min, self.max, 0, 1 ) * self._back_geo.width

        self._back_geo.draw ( region )
        self._front_geo.draw ( region )



class BGLLayoutBase ( BGLWidget ):
    def __init__ ( self ):
        BGLWidget.__init__ ( self )
        self._widgets: List[ BGLWidget ] = list ( )

    def add_widget ( self, widget ):
        self._widgets.append ( widget )

    def layout_widgets ( self, region ):
        raise NotImplementedError ( )

    def handle_event ( self, region, event: bpy.types.Event ):
        self.layout_widgets ( region )
        for wdgt in self._widgets:
            wdgt.handle_event ( region, event )

    def draw ( self, region ):
        self.layout_widgets ( region )
        for wdgt in self._widgets:
            wdgt.draw ( region )

    def get_bound( self, region: BGLRegion ):
        if self._widgets:
            bound = self._widgets[ 0 ].get_bound ( region )
            self.layout_widgets ( region )
            for wgdt in self._widgets[ 1: ]:
                bound += wgdt.get_bound ( region )
        else:
            bound = BGLBound ( )

        return bound



class BGLLayoutH ( BGLLayoutBase ):
    def __init__ ( self ):
        BGLLayoutBase.__init__ ( self )
        self.spacing = 5
        self.fill_region = False

    def layout_widgets ( self, region ):
        pos = BGLCoord ( *self.position )

        spacing = self.spacing
        if self.fill_region:
            total_widgets_width = 0
            pos.x = region.bound.min.x
            for wdgt in self._widgets:
                total_widgets_width += wdgt.get_bound ( region ).width
            free_space = region.bound.width - total_widgets_width
            spacing = max ( free_space / ( len ( self._widgets) - 1 ), self.spacing )

        for wdgt in self._widgets:
            wdgt.position = BGLCoord ( *pos )
            pos.x += wdgt.get_bound ( region ).width + spacing



class BGLLayoutV ( BGLLayoutBase ):
    def __init__ ( self ):
        BGLLayoutBase.__init__ ( self )
        self.spacing = 5
        self._fill_region = False

    def layout_widgets ( self, region ):
        pos = BGLCoord ( *self.position )
        spacing = self.spacing
        if self.fill_region:
            pos.y = region.bound.min.y
            total_widgets_height = 0
            for wdgt in self._widgets:
                total_widgets_height += wdgt.get_bound ( region ).height
            free_space = region.bound.height - total_widgets_height
            spacing = max ( free_space / ( len ( self._widgets) - 1 ), self.spacing )

        for wdgt in self._widgets:
            wdgt.position = BGLCoord ( *pos )
            pos.y += wdgt.get_bound ( region ).height + spacing
