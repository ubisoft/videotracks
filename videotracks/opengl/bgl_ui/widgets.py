# -*- coding: utf-8 -*-
import bpy
from typing import Callable, Union, Tuple

from .types import BGLBound, BGLColor, BGLCoord, BGLRegion, BGLPropValue
from.geometries import BGLRect, BGLText
from . import shaders



def _nop ( *args, **kwargs ):
    pass


class BGLWidget:
    def __init__ ( self, position: BGLCoord = None ):
        if position is None:
            self._position = BGLPropValue ( BGLCoord ( ) )
        else:
            self._position = BGLPropValue ( position )

    @property
    def position ( self ):
        return  self._position.value

    @position.setter
    def position ( self, value: BGLCoord ):
        self._position.value = value

    def draw ( self, region: BGLRegion ):
        pass

    def handle_event ( self, region: BGLRegion, event : bpy.types.Event ) -> bool:
        return False



class BGLButton ( BGLWidget ):
    def __init__( self, position: BGLCoord, width, height, text = "Button" ):
        BGLWidget.__init__ ( self, position )

        self._width = width
        self._height = height

        self._color = BGLPropValue ( BGLColor ( .5, .5, .5 ) )
        self._hightlight_color = self._color ** .8

        self._geometry = BGLRect ( position.x, position.y , width, height )
        self._text_geometry = BGLText ( self._geometry.get_bound ( ).center, text = text, center_text = True )

        self._highlighted = False
        self._on_clicked_callback = _nop

        self._prev_click_time = 0
        self._is_pushed = False

    @property
    def color ( self ):
        return self._color.value

    @color.setter
    def color ( self, value ):
        self._color.value = value

    @property
    def highlight_color ( self ):
        return self._hightlight_color.value

    @highlight_color.setter
    def highlight_color ( self, value ):
        self._hightlight_color.value = value

    @property
    def text ( self ):
        return self._text_geometry.text

    @text.setter
    def text ( self, value ):
        self._text_geometry.text.value = value

    @property
    def clicked_callback ( self ):
        return self._on_clicked_callback

    @clicked_callback.setter
    def clicked_callback ( self, callback: Callable[ [ "BLButton" ], None ] ):
        if callback is None:
            self._on_clicked_callback = _nop
        else:
            self._on_clicked_callback = callback


    def handle_event( self, region, event : bpy.types.Event) -> bool:
        mouse_pos = region.mouse_to_region ( BGLCoord ( event.mouse_x, event.mouse_y ) )
        if event.type == "LEFTMOUSE":
            if self._geometry.is_over ( mouse_pos, region ):
                if event.value == "PRESS":
                    self._is_pushed = True
                elif event.value == "RELEASE":
                    if self._is_pushed:
                        self._on_clicked_callback ( )
                    self._is_pushed = False

        elif event.type == "MOUSEMOVE":
            if self._geometry.is_over ( mouse_pos, region ):
                self._highlighted = True
            else:
                self._highlighted = False

        return False


    def draw ( self, region ):
        shaders.UNIFORM_SHADER_2D.bind ( )
        if self._highlighted:
            shaders.UNIFORM_SHADER_2D.uniform_float ( "color", self.highlight_color )
        else:
            shaders.UNIFORM_SHADER_2D.uniform_float ( "color", self.color )

        self._geometry.draw ( shaders.UNIFORM_SHADER_2D, region )
        self._text_geometry.draw ( None, region )