# -*- coding: utf-8 -*-
import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

def remap ( value, old_min, old_max, new_min, new_max ):
    value = clamp(value, old_min, old_max)
    old_range = old_max - old_min
    if old_range == 0:
        new_value = new_min
    else:
        new_range = new_max - new_min
        new_value = (((value - old_min) * new_range) / old_range) + new_min

    return new_value

def clamp(value, minimum, maximum):
    return min(max(value, minimum), maximum)


def clamp_to_region(x, y, region, bound ):
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

