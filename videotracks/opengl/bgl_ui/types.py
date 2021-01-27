# -*- coding: utf-8 -*-
import bpy
from .utils import clamp, clamp_to_region


class BGLType:
    def __init__(self):
        pass

    def __iter__(self):
        raise NotImplementedError ( )

    def __add__(self, other):
        raise NotImplementedError ( )

    def __sub__ ( self, other ):
        raise NotImplementedError ( )

    def __pow__(self, power, modulo=None):
        raise NotImplementedError ( )



class BGLCoord ( BGLType ):
    def __init__( self, x = 0, y = 0 ):
        BGLType.__init__( self )
        self.x = x
        self.y = y

    def __iter__ ( self ):
        return iter ( ( self.x, self.y ) )

    def __add__ ( self, other ):
        return BGLCoord ( self.x + other.x, self.y + other.y )

    def __sub__ ( self, other ):
        return BGLCoord ( self.x - other.x, self.y - other.y )

    def __pow__ ( self, power, modulo=None ):
        return BGLCoord ( self.x ** power, self.y ** power )

    def __repr__(self):
        return f"{type ( self ).__name__} ( {self.x}, {self.y} )"



class BGLColor ( BGLType ):
    def __init__( self, r = 1., g = 1., b = 1., a = 1. ):
        BGLType.__init__ ( self )
        self._r = r
        self._g = g
        self._b = b
        self._a = a

    @property
    def r ( self ):
        return self._r

    @r.setter
    def r ( self, r ):
        self._r = r

    @property
    def g ( self ):
        return self._g

    @g.setter
    def g ( self, g ):
        self._g =g

    @property
    def b ( self ):
        return self._b

    @b.setter
    def b ( self, b ):
        self._b = b

    @property
    def a ( self ):
        return  self._a

    @a.setter
    def a ( self, a ):
        self._a = a

    def __iter__ ( self ):
        return iter ( ( self._r, self._g, self._b, self._a ) )

    def __add__ ( self, other ):
        return BGLColor ( self.r + other.r,
                          self.g + other.g,
                          self.b + other.b,
                          self.a + other.a )

    def __sub__ ( self, other ):
        return BGLColor ( self.r - other.r,
                          self.g - other.g,
                          self.b - other.b,
                          self.a - other.a )

    def __pow__(self , power, modulo=None ):
        return BGLColor ( self.r ** power,
                          self.g ** power,
                          self.b ** power,
                          self.a )

    def __repr__(self):
        return f"{type ( self ).__name__} ( {self.r}, {self.g}, {self.b}, {self.a} )"



class BGLBound:
    def __init__ ( self, min_position = None, max_position = None):
        if min_position is None:
            self.min = BGLCoord ( -99999, -99999 )
        else:
            self.min = min_position

        if max_position is None:
            self.max = BGLCoord ( 99999, 99999 )
        else:
            self.max = max_position

    @property
    def width ( self ):
        return  self.max.x - self.min.x

    @property
    def height ( self ):
        return  self.max.y - self.min.y

    @property
    def center ( self ):
        return BGLCoord ( self.min.x + self.width * .5, self.min.y + self.height * .5 )

    def clamp ( self, position: BGLCoord ):
        return BGLCoord ( clamp ( position.x, self.min.x, self.max.x ), clamp ( position.y, self.min.y, self.max.y ) )

    def fully_contains ( self, bound: "BGLBound" ):
        """
        Check if the bound fully englobes the other bound.
        """
        if self.min.x <= bound.min.x and self.min.y <= bound.min.y and self.max.x >= bound.max.x and self.max.y >= bound.max.y:
            return True

        return False

    def partially_contains ( self, bound: "BGLBound" ):
        if self.min.x <= bound.min.x <=self.max.x and self.min.y <= bound.min.y <=self.max.y:
            return True
        elif self.min.x <= bound.max.x <=self.max.x and self.min.y <= bound.max.y <=self.max.y:
            return True

        return False



class BGLTransform:
    def __init__ ( self ):
        pass

    def apply_transform ( self, region: "BGLRegion", position: BGLCoord, clip_to_region = True ):
        return BGLCoord ( position.x, position.y )



class BGLViewToRegion ( BGLTransform ):
    def __init__ ( self, apply_to_x = True, apply_to_y = True ):
        BGLTransform.__init__ ( self )
        self.apply_to_x = apply_to_x
        self.apply_to_y = apply_to_y

    def apply_transform( self, region: "BGLRegion", position: BGLCoord, clip_to_region = True ):
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
    def bound ( self ) -> BGLBound:
        return BGLBound ( BGLCoord ( self._crops[ 0 ], self._crops[ 1 ] ), BGLCoord ( self.bl_region.width - self._crops[ 2 ], self.bl_region.height - self._crops[ 3 ] ) )

    def view_to_region ( self, position: BGLCoord, region_clip = True ) -> BGLCoord:
        if region_clip:
            position = clamp_to_region ( position.x, position.y, self.bl_region, self.bound )
        return BGLCoord ( *self.bl_region.view2d.view_to_region ( *position ) )

    def mouse_to_region ( self, position: BGLCoord ( ) ):
        return position - BGLCoord ( self.bl_region.x, self.bl_region.y )



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