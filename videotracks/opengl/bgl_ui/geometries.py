# -*- coding: utf-8 -*-
from gpu_extras.batch import batch_for_shader
import bpy, blf
from mathutils import Vector

from .types import BGLColor, BGLBound, BGLRegion, BGLCoord, BGLPropValue

class BGLGeometry:
    def __init__ ( self ):
        pass

    def get_bound ( self, region: BGLRegion = None ) -> BGLBound:
        pass

    def is_over ( self, position: BGLCoord, region: BGLRegion ) -> bool:
        pass

    def draw ( self, shader, region: BGLRegion ):
        pass



class BGLRect ( BGLGeometry ):
    def __init__ ( self, x, y, width, height ):
        BGLGeometry.__init__ ( self )
        self._lo = BGLCoord ( x, y )
        self._hi = BGLCoord ( x + width, y + height )

    def get_bound ( self, region: BGLRegion = None ):
        if region is not None:
            return BGLBound ( BGLCoord ( *region.transform.apply_transform ( region, self._lo ) ), BGLCoord ( *region.transform.apply_transform ( region, self._hi ) ) )
        else:
            return BGLBound ( self._lo, self._hi )

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
    def __init__ ( self, position: BGLCoord, size = 11, text = "Label", color = None, center_text = False ):
        BGLGeometry.__init__ ( self )
        self.size = size
        self._pos = BGLPropValue ( position )
        self._text = BGLPropValue ( text )
        self._color = BGLPropValue ( BGLColor ( 1, 1, 1 ) if color is None else color )
        self.center_text = center_text

    @property
    def position ( self ):
        return  self._pos.value

    @position.setter
    def position ( self, value: BGLCoord ):
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
