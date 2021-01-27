# -*- coding: utf-8 -*-
from typing import Callable, Union, Tuple
import time

import bpy, blf
from mathutils import Vector

from enum import Flag, auto

from .utils import Bound, Color, clamp_to_region, Position2d
from . import shaders
from gpu_extras.batch import batch_for_shader


def _nop ( *args, **kwargs ):
    pass

"""
class BGLPivot ( Flag ):
    CENTER = auto ( )
    BOTTOM = auto ( )
    TOP = auto ( )
    LEFT = auto ( )
    RIGHT = auto ( )
"""

class BGLTransform:
    def __init__ ( self ):
        pass

    def apply_transform ( self, region: "BGLRegion",position: Position2d, clip_to_region = True ):
        return Position2d ( position.x, position.y )



class BGLViewToRegion ( BGLTransform ):
    def __init__ ( self, apply_to_x = True, apply_to_y = True ):
        BGLTransform.__init__ ( self )
        self.apply_to_x = apply_to_x
        self.apply_to_y = apply_to_y

    def apply_transform( self, region: "BGLRegion", position: Position2d, clip_to_region = True ):
        new_pos = region.view_to_region ( position, clip_to_region )
        if self.apply_to_x is False:
            new_pos.x = position.x

        if self.apply_to_y is False:
            new_pos.y = position.y

        return new_pos


class BGLRegion:
    def __init__ ( self, crop_left = 0, crop_bottom = 0, crop_right = 0, crop_top = 0 ):
        self._crops = ( crop_left, crop_bottom, crop_right, crop_top )
        self.bl_region: bpy.types.Region = None
        self.transform = BGLTransform ( )

    @property
    def bound ( self ) -> Bound:
        return Bound ( Position2d ( self._crops[ 0 ], self._crops[ 1 ] ), Position2d (  self.bl_region.width - self._crops[ 2 ], self.bl_region.height - self._crops[ 3 ] ) )

    def view_to_region ( self, position: Position2d, region_clip = True ) -> Position2d:
        if region_clip:
            position = clamp_to_region ( position.x, position.y, self.bl_region, self.bound )
        return Position2d ( *self.bl_region.view2d.view_to_region ( *position ) )

    def mouse_to_region ( self, position: Position2d ( ) ):
        return position - Position2d ( self.bl_region.x, self.bl_region.y )



class BGLGeometry:
    def __init__ ( self ):
        pass

    def get_bound ( self, region: BGLRegion = None ) -> Bound:
        pass

    def is_over ( self, position: Position2d, region: BGLRegion ) -> bool:
        pass

    def draw ( self, shader, region: BGLRegion ):
        pass



class BGLRect ( BGLGeometry ):
    def __init__ ( self, x, y, width, height ):
        BGLGeometry.__init__ ( self )
        self._lo = Position2d ( x, y )
        self._hi = Position2d ( x + width, y + height )

    def get_bound ( self, region: BGLRegion = None ):
        if region is not None:
            return Bound ( Position2d ( *region.transform.apply_transform ( region, self._lo ) ), Position2d ( *region.transform.apply_transform ( region, self._hi ) ) )
        else:
            return Bound ( self._lo, self._hi )

    def is_over( self, position, region: BGLRegion ) -> bool:
        lo = region.transform.apply_transform ( region, self._lo )
        hi = region.transform.apply_transform ( region, self._hi )

        if  lo.x <= position.x < hi.x and lo.y <= position.y <= hi.y:
            return True

        return False

    def draw ( self, shader, region: BGLRegion ):
        lo = region.transform.apply_transform ( region, self._lo )
        hi = region.transform.apply_transform ( region, self._hi )

        batch = batch_for_shader ( shader, "TRIS", { "pos": [ Vector ( list ( lo ) ),
                                                              Vector ( [ hi.x, lo.y ] ),
                                                              Vector ( list ( hi ) ),
                                                              Vector ( [ lo.x, hi.y ] ) ] },
                                   indices = [ ( 0, 1, 3 ), ( 1, 2, 3 ) ] )
        batch.draw ( shader )



class BGLText ( BGLGeometry ):
    def __init__ ( self, position: Position2d, size = 11, text = "Label", color = None, center_text = False ):
        BGLGeometry.__init__ ( self )
        self.size = size
        self._pos = BGLPropValue ( position )
        self._text = BGLPropValue ( text )
        self._color = BGLPropValue ( Color ( 1, 1, 1 ) if color is None else color )
        self.center_text = center_text

    @property
    def position ( self ):
        return  self._pos.value

    @position.setter
    def position ( self, value: Position2d ):
        self._pos = BGLPropValue ( value )


    @property
    def text ( self ):
        return  self._text.value

    @text.setter
    def text ( self, value ):
        self._text.value = value

    @property
    def color ( self ):
        return  self._color.value

    @color.setter
    def color ( self, value ):
        self._color.value = value

    @property
    def height ( self ):
        return blf.dimensions ( 0, self.text )[ 1 ]

    @property
    def width ( self ):
        return blf.dimensions ( 0, self.text )[ 0 ]

    def get_bound ( self, region: BGLRegion = None ):
        text_width, text_height = blf.dimensions ( 0, self.text )
        pos = self.position
        if region is not None:
            pos = region.transform.apply_transform ( region, self.position, False )
        if self.center_text:
            half_width = text_width * .5
            half_height = text_height * .5
            return Bound ( Position2d ( pos.x - half_width, pos.y - half_height), Position2d ( pos.x + half_width, pos.y + half_height ) )
        else:
            return Bound ( Position2d ( pos.x, pos.y ), Position2d ( pos.x + text_width, pos.y + text_height ) )

    def is_over( self, position: Position2d, region: BGLRegion ) -> bool:
        bound = self.get_bound ( region )
        if  bound.min.x <= position.x < bound.max.x and bound.min.y <= position.y <= bound.max.y:
            return True

        return False

    def draw ( self, shader, region ):
        blf.size ( 0, self.size, 72 )
        bound = self.get_bound ( region )
        if region.bound.fully_contains ( bound ):
            blf.position ( 0, bound.min.x, bound.min.y, 0 )
            blf.draw ( 0, self.text )



class BGLPropValue:
    def __init__( self, value ):
        if isinstance ( value, BGLPropValue ):
            self._value = value._value
        else:
            self._value = value

    @property
    def value ( self ):
        if callable ( self._value ):
            return self._value ( )
        else:
            return self._value

    @value.setter
    def value ( self, value ):
        self._value = value

    def __add__ ( self, other ):
        return BGLPropValue ( lambda s = self, o = other: s.value + o.value )

    def __sub__ ( self, other ):
        return BGLPropValue ( lambda s = self, o = other: s.value - o.value )

    def __pow__(self, power, modulo=None):
        return BGLPropValue ( lambda s = self, p = power: s.value ** p )



class BGLWidget:
    def __init__ ( self, position: Position2d = None ):
        if position is None:
            self._position = BGLPropValue ( Position2d ( ) )
        else:
            self._position = BGLPropValue ( position )

    @property
    def position ( self ):
        return  self._position.value

    @position.setter
    def position ( self, value: Position2d ):
        self._position.value = value

    def draw ( self, region: BGLRegion ):
        pass

    def handle_event ( self, region: BGLRegion, event : bpy.types.Event ) -> bool:
        return False



class BGLButton ( BGLWidget ):
    def __init__( self, position: Position2d, width, height, text = "Button" ):
        BGLWidget.__init__ ( self, position )

        self._width = width
        self._height = height

        self._color = BGLPropValue ( Color ( .5, .5, .5 ) )
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
        mouse_pos = region.mouse_to_region ( Position2d ( event.mouse_x, event.mouse_y ) )
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