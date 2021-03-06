# -*- coding: utf-8 -*-

"""
Reflexion:

Maybe geometry should not have a defined position. The widgets are responsible for drawings and also have a position. This is redondant.

Move Shader draw calls in here part in there

Todo:
    - allow caching of batch so we don't recreate them at each draw call. Maybe via setting a callback to a BGLProp.
"""

from typing import Callable, Union

import math
from gpu_extras.batch import batch_for_shader
import bpy, blf, bgl
from mathutils import Vector

from .types import BGLColor, BGLBound, BGLRegion, BGLCoord, BGLPropValue, BGLProp, BGLImageManager
from .shaders import BGLImageShader, BGLUniformShader

from videotracks.utils import utils


class BGLGeometry:
    position = BGLProp(BGLCoord())

    def __init__(self, **prop_values):
        for k, v in prop_values.items():
            setattr(self, k, v)

    def get_bound(self, region: BGLRegion = None) -> BGLBound:
        return BGLBound()

    def is_over(self, position: BGLCoord, region: BGLRegion) -> bool:
        return False

    def draw(self, region: BGLRegion):
        pass


class BGLRect(BGLGeometry):
    color = BGLProp(BGLColor(0.1, 0.4, 0.4))
    width = BGLProp(10)
    height = BGLProp(10)

    def get_bound(self, region: BGLRegion = None):
        lo = BGLCoord(self.position.x, self.position.y)
        hi = BGLCoord(self.position.x + self.width, self.position.y + self.height)

        if region is not None:
            return BGLBound(
                BGLCoord(*region.transform.apply_transform(region, lo)),
                BGLCoord(*region.transform.apply_transform(region, hi)),
            )
        else:
            return BGLBound(lo, hi)

    def is_over(self, position, region: BGLRegion) -> bool:
        bound = self.get_bound(region)
        if bound.min.x <= position.x <= bound.max.x and bound.min.y <= position.y <= bound.max.y:
            return True

        return False

    def draw(self, region: BGLRegion):
        bound = self.get_bound(region)
        batch = BGLUniformShader.create_batch(
            "TRIS",
            {
                "pos": [
                    Vector(list(bound.min)),
                    Vector([bound.max.x, bound.min.y]),
                    Vector(list(bound.max)),
                    Vector([bound.min.x, bound.max.y]),
                ]
            },
            indices=[(0, 1, 3), (1, 2, 3)],
        )

        with BGLUniformShader() as shader:
            # shader.set_color(utils.sRGBColor(self.color))
            shader.set_color(self.color.to_sRGB())
            shader.draw_batch(batch)


class BGLRectLine(BGLRect):
    line_width = BGLProp(5)

    def draw(self, region: BGLRegion):
        bound = self.get_bound(region)
        batch = BGLUniformShader.create_batch(
            "LINES",
            {
                "pos": [
                    Vector(list(bound.min)),
                    Vector([bound.max.x, bound.min.y]),
                    Vector(list(bound.max)),
                    Vector([bound.min.x, bound.max.y]),
                ]
            },
            indices=[(0, 1), (1, 2), (2, 3), (3, 0)],
        )

        with BGLUniformShader() as shader:
            bgl.glLineWidth(self.line_width)
            # shader.set_color(utils.sRGBColor(self.color))
            # bgl.glLineWidth(5)
            shader.set_color(self.color.to_sRGB())
            shader.draw_batch(batch)
            bgl.glLineWidth(1)


class BGLCircle(BGLGeometry):
    color = BGLProp(BGLColor())
    radius = BGLProp(1)
    division = BGLProp(12)

    def get_bound(self, region: BGLRegion = None):
        pos = self.position
        if region is not None:
            pos = region.transform.apply_transform(region, self.position)

        tmp = BGLCoord(self.radius, self.radius)

        return BGLBound(pos - tmp, pos + tmp)

    def is_over(self, position, region: BGLRegion) -> bool:
        my_position = region.transform.apply_transform(region, self.position)
        if (my_position - position).length2() <= self.radius * self.radius:
            return True

        return False

    def draw(self, region: BGLRegion):
        points = list()
        indices = list()
        num_pts = self.division
        step = math.pi * 2.0 / num_pts
        # first point in the list is origin.
        points.append(Vector(self.position))
        for i in range(num_pts):
            t = i * step
            points.append(
                Vector([math.cos(t) * self.radius + self.position.x, math.sin(t) * self.radius + self.position.y])
            )

        for i in range(num_pts - 1):
            indices.append((0, i + 1, i + 2))
        indices.append((0, num_pts, 1))  # Last Face

        batch = BGLUniformShader.create_batch("TRIS", {"pos": points}, indices=indices)
        with BGLUniformShader() as shader:
            shader.set_color(self.color)
            shader.draw_batch(batch)


class BGLText(BGLGeometry):
    size = BGLProp(11)
    text = BGLProp("Label")
    color = BGLProp(BGLColor(0.9, 0.4, 0.4))
    centered = BGLProp(False)

    @property
    def height(self):
        return blf.dimensions(0, self.text)[1]

    @property
    def width(self):
        return blf.dimensions(0, self.text)[0]

    def get_bound(self, region: BGLRegion = None):
        text_width, text_height = blf.dimensions(0, self.text)
        pos = self.position
        if region is not None:
            pos = region.transform.apply_transform(region, self.position, True)
        if self.centered:
            half_width = text_width * 0.5
            half_height = text_height * 0.5
            return BGLBound(
                BGLCoord(pos.x - half_width, pos.y - half_height), BGLCoord(pos.x + half_width, pos.y + half_height)
            )
        else:
            return BGLBound(BGLCoord(pos.x, pos.y), BGLCoord(pos.x + text_width, pos.y + text_height))

    def is_over(self, position: BGLCoord, region: BGLRegion) -> bool:
        bound = self.get_bound(region)
        if bound.min.x <= position.x < bound.max.x and bound.min.y <= position.y <= bound.max.y:
            return True

        return False

    def drawAdv(self, region, rotation=0):
        fontid = 0
        # https://blenderartists.org/t/blf-clipping-aspect-rotation-shadow-blur/544985/4
        if 0 != rotation:
            blf.rotation(fontid, rotation)
            blf.enable(fontid, blf.ROTATION)
        self.draw(region)
        if 0 != rotation:
            blf.disable(fontid, blf.ROTATION)

    def draw(self, region):
        fontid = 0
        blf.size(fontid, self.size, 72)
        bound = self.get_bound(region)
        if region.bound.fully_contains(bound):
            blf.position(fontid, bound.min.x, bound.min.y + bound.height * 0.5, 0)
            blf.color(fontid, self.color.r, self.color.g, self.color.b, 1.0)
            # print(f" drawn text: {self.text}")
            blf.draw(fontid, self.text)


class BGLTexture(BGLRect):
    image = BGLProp(None)  # BGLImageManager.BGLImage
    width = BGLProp(10)
    height = BGLProp(10)

    def get_bound(self, region: BGLRegion = None):
        if self.image is None:
            return BGLBound()
        else:
            return BGLRect.get_bound(self, region)

    def draw(self, region: BGLRegion):
        if self.image is None:
            return
        bound = self.get_bound(region)
        batch = BGLImageShader.create_batch(
            "TRIS",
            {
                "pos": [
                    Vector(list(bound.min)),
                    Vector([bound.max.x, bound.min.y]),
                    Vector(list(bound.max)),
                    Vector([bound.min.x, bound.max.y]),
                ],
                "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
            },
            indices=[(0, 1, 3), (1, 2, 3)],
        )

        with BGLImageShader() as shader:
            shader.set_image(self.image)
            shader.draw_batch(batch)

