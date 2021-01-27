# -*- coding: utf-8 -*-
import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

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



class Position2d ( BGLType ):
    def __init__( self, x = 0, y = 0 ):
        BGLType.__init__( self )
        self.x = x
        self.y = y

    def __iter__ ( self ):
        return iter ( ( self.x, self.y ) )

    def __add__ ( self, other ):
        return Position2d ( self.x + other.x, self.y + other.y )

    def __sub__ ( self, other ):
        return Position2d ( self.x - other.x, self.y - other.y )

    def __pow__ ( self, power, modulo=None ):
        return Position2d ( self.x ** power, self.y ** power )

    def __repr__(self):
        return f"{type ( self ).__name__} ( {self.x}, {self.y} )"



class Color ( BGLType ):
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
        return Color ( self.r + other.r,
                       self.g + other.g,
                       self.b + other.b,
                       self.a + other.a )

    def __sub__ ( self, other ):
        return Color ( self.r - other.r,
                       self.g - other.g,
                       self.b - other.b,
                       self.a - other.a )

    def __pow__(self , power, modulo=None ):
        return Color ( self.r ** power,
                       self.g ** power,
                       self.b ** power,
                       self.a )

    def __repr__(self):
        return f"{type ( self ).__name__} ( {self.r}, {self.g}, {self.b}, {self.a} )"



class Bound:
    def __init__ ( self, min_position = None, max_position = None):
        if min_position is None:
            self.min = Position2d ( -99999, -99999 )
        else:
            self.min = min_position

        if max_position is None:
            self.max = Position2d ( 99999, 99999 )
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
        return Position2d ( self.min.x + self.width * .5, self.min.y + self.height * .5 )

    def clamp ( self, position: Position2d ):
        return Position2d ( clamp ( position.x, self.min.x, self.max.x ), clamp ( position.y, self.min.y, self.max.y ) )

    def fully_contains ( self, bound: "Bound" ):
        """
        Check if the bound fully englobes the other bound.
        """
        if self.min.x <= bound.min.x and self.min.y <= bound.min.y and self.max.x >= bound.max.x and self.max.y >= bound.max.y:
            return True

        return False

    def partially_contains ( self, bound: "Bound" ):
        if self.min.x <= bound.min.x <=self.max.x and self.min.y <= bound.min.y <=self.max.y:
            return True
        elif self.min.x <= bound.max.x <=self.max.x and self.min.y <= bound.max.y <=self.max.y:
            return True

        return False


def clamp(value, minimum, maximum):
    return min(max(value, minimum), maximum)


def clamp_to_region(x, y, region, bound = Bound ( ) ):
    l_x, l_y = region.view2d.region_to_view ( bound.min.x, bound.min.y )
    h_x, h_y = region.view2d.region_to_view (bound.max.x -1, bound.max.y - 1 )
    return clamp(x, l_x, h_x), clamp(y, l_y, h_y)


def get_region_at_xy(context, x, y ):
    """
    Does not support quadview right now

    :param context:
    :param x:
    :param y:
    :return: the region and the area containing this region
    """
    for area in context.screen.areas:
        # is_quadview = len ( area.spaces.active.region_quadviews ) == 0
        i = -1
        for region in area.regions:
            if region.type == "WINDOW":
                i += 1
                if region.x <= x < region.width + region.x and region.y <= y < region.height + region.y:

                    return region, area

    return None, None


class Mesh2D:
    def __init__(self, vertices=None, indices=None, texcoords=None):
        self._vertices = list() if vertices is None else vertices
        self._indices = list() if indices is None else indices
        self._texcoords = list() if texcoords is None else texcoords

        self._lo_bound = min ( self._vertices )
        self._hi_bound = max ( self._vertices )

    @property
    def vertices(self):
        return list(self._vertices)

    @property
    def indices(self):
        return list(self._indices)

    @property
    def texcoords(self):
        return list(self._texcoords)

    @property
    def bound ( self ):
        return self._lo_bound, self._hi_bound

    def draw(self, shader, region=None, use_region_to_view = False, draw_types="TRIS"):
        transformed_vertices = self._vertices
        if region:
            if use_region_to_view:
                transformed_vertices = [
                    region.view2d.region_to_view ( x, y ) for x, y in transformed_vertices
                ]
            else:
                transformed_vertices = [
                    region.view2d.view_to_region(*clamp_to_region(x, y, region), clip=True) for x, y in transformed_vertices
                ]

        batch = batch_for_shader(shader, draw_types, {"pos": transformed_vertices}, indices=self._indices)
        batch.draw(shader)



def build_rectangle_mesh(position, width, height, as_lines=False):
    """

    :param position:
    :param width:
    :param height:
    :param region: if region is specified this will transform the vertices into the region's view. This allow for pan and zoom support
    :return:
    """
    x1, y1 = position.x, position.y
    x2, y2 = position.x + width, position.y
    x3, y3 = position.x, position.y + height
    x4, y4 = position.x + width, position.y + height

    vertices = ((x1, y1), (x2, y2), (x3, y3), (x4, y4))
    if as_lines:
        indices = ((0, 1), (0, 2), (2, 3), (1, 3))
    else:
        indices = ((0, 1, 2), (2, 1, 3))

    return Mesh2D(vertices, indices)

