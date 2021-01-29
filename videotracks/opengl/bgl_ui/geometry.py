# -*- coding: utf-8 -*-

"""
Reflexion:

Maybe geometry should not have a defined position. The widgets are responsible for drawings and also have a position. This is redondant.
"""

from typing import Callable, Union

import math
from gpu_extras.batch import batch_for_shader
import bpy, blf
from mathutils import Vector

from .types import BGLColor, BGLBound, BGLRegion, BGLCoord, BGLPropValue


class BGLGeometry:
    def __init__ ( self, position: Union[ BGLCoord, Callable ] = BGLCoord ( ) ):
        self._position = BGLPropValue ( position )

    @property
    def position ( self ):
        return  self._position.value

    @position.setter
    def position ( self, value ):
        self._position = BGLPropValue ( value )

    def get_bound ( self, region: BGLRegion = None ) -> BGLBound:
        pass

    def is_over ( self, position: BGLCoord, region: BGLRegion ) -> bool:
        pass

    def draw ( self, shader, region: BGLRegion ):
        pass



class BGLRect ( BGLGeometry ):
    def __init__ ( self, position, width, height ):
        BGLGeometry.__init__ ( self, position )
        self.width = width
        self.height = height

    def get_bound ( self, region: BGLRegion = None ):
        lo = BGLCoord ( self.position.x, self.position.y )
        hi = BGLCoord ( self.position.x + self.width, self.position.y + self.height )

        if region is not None:
            return BGLBound ( BGLCoord ( *region.transform.apply_transform ( region, lo ) ), BGLCoord ( *region.transform.apply_transform ( region, hi ) ) )
        else:
            return BGLBound ( lo, hi )

    def is_over( self, position, region: BGLRegion ) -> bool:
        bound = self.get_bound ( region )
        if  bound.min.x <= position.x < bound.max.x and bound.min.y <= position.y <= bound.max.y:
            return True

        return False

    def draw ( self, shader, region: BGLRegion ):
        bound = self.get_bound ( region )

        batch = batch_for_shader ( shader, "TRIS", { "pos": [ Vector ( list ( bound.min ) ),
                                                              Vector ( [ bound.max.x, bound.min.y ] ),
                                                              Vector ( list ( bound.max ) ),
                                                              Vector ( [ bound.min.x, bound.max.y ] ) ] },
                                   indices = [ ( 0, 1, 3 ), ( 1, 2, 3 ) ] )
        batch.draw ( shader )



class BGLCircle ( BGLGeometry ):
    def __init__ ( self, position: BGLCoord, radius, division = 12 ):
        BGLGeometry.__init__ ( self, position )
        self.radius = radius
        self._division = max ( division, 4 )

    def get_bound ( self, region: BGLRegion = None ):
        pos = self.position
        if region is not None:
            pos = region.transform.apply_transform ( region, self.position )

        tmp = BGLCoord ( self.radius, self.radius )

        return BGLBound ( pos - tmp, pos + tmp )

    def is_over( self, position, region: BGLRegion ) -> bool:
        my_position = region.transform.apply_transform ( region, self.position )
        if ( my_position - position ).length2 ( ) <= self.radius * self.radius:
            return True

        return False

    def draw ( self, shader, region: BGLRegion ):
        points = list ( )
        indices = list ( )
        num_pts = self._division
        step = math.pi * 2. / num_pts
        # first point in the list is origin.
        points.append ( Vector ( self.position ) )
        for i in range ( num_pts ):
            t = i * step
            points.append ( Vector ( [ math.cos ( t ) * self.radius + self.position.x, math.sin ( t ) * self.radius + self.position.y  ] ) )

        for i in range ( num_pts - 1 ):
            indices.append ( ( 0, i + 1 ,  i + 2 ) )
        indices.append ( ( 0, num_pts, 1 ) ) # Last Face

        batch = batch_for_shader ( shader, "TRIS", { "pos": points }, indices = indices )
        batch.draw ( shader )



class BGLText ( BGLGeometry ):
    def __init__ ( self, position: BGLCoord, size = 11, text = "Label", color = None, center_text = False ):
        BGLGeometry.__init__ ( self, position )
        self.size = size
        self._text = BGLPropValue ( text )
        self._color = BGLPropValue ( BGLColor ( 1, 1, 1 ) if color is None else color )
        self.center_text = center_text


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
            return BGLBound ( BGLCoord ( pos.x - half_width, pos.y - half_height ), BGLCoord ( pos.x + half_width, pos.y + half_height ) )
        else:
            return BGLBound ( BGLCoord ( pos.x, pos.y ), BGLCoord ( pos.x + text_width, pos.y + text_height ) )

    def is_over( self, position: BGLCoord, region: BGLRegion ) -> bool:
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
