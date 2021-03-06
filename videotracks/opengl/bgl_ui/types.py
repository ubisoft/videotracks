# -*- coding: utf-8 -*-
import math
from copy import deepcopy
from pathlib import Path
from typing import Any

import bpy
import bgl
from .utils import clamp, clamp_to_region


class BGLCoord:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def length2(self):
        return self.x * self.x + self.y * self.y

    def __iter__(self):
        return iter((self.x, self.y))

    def __add__(self, other):
        v1 = self.x
        v2 = self.y
        try:
            i = iter(other)
            v1 += next(i, 0)
            v2 += next(i, 0)
        except TypeError:
            v1 += other
            v2 += other

        return BGLCoord(v1, v2)

    def __mul__(self, other):
        v1 = self.x
        v2 = self.y
        try:
            i = iter(other)
            v1 *= next(i, 0)
            v2 *= next(i, 0)
        except TypeError:
            v1 *= other
            v2 *= other

        return BGLCoord(v1, v2)

    def __sub__(self, other):
        v1 = self.x
        v2 = self.y
        try:
            i = iter(other)
            v1 -= next(i, 0)
            v2 -= next(i, 0)
        except TypeError:
            v1 -= other
            v2 -= other

        return BGLCoord(v1, v2)

    def __pow__(self, other, modulo=None):
        v1 = self.x
        v2 = self.y
        try:
            i = iter(other)
            v1 **= next(i, 0)
            v2 **= next(i, 0)
        except TypeError:
            v1 **= other
            v2 **= other

        return BGLCoord(v1, v2)

    def __repr__(self):
        return f"{type ( self ).__name__} ( {self.x}, {self.y} )"


class BGLColor:
    def __init__(self, r=1.0, g=1.0, b=1.0, a=1.0):
        self._r = r
        self._g = g
        self._b = b
        self._a = a

    @property
    def r(self):
        return self._r

    @r.setter
    def r(self, r):
        self._r = r

    @property
    def g(self):
        return self._g

    @g.setter
    def g(self, g):
        self._g = g

    @property
    def b(self):
        return self._b

    @b.setter
    def b(self, b):
        self._b = b

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, a):
        self._a = a

    def to_linear(self):
        gamma = 0.45
        # return BGLColor(pow(self._r, gamma), pow(self._g, gamma), pow(self._b, gamma), self._a * 1.0)
        return BGLColor(pow(self._r, gamma), pow(self._g, gamma), pow(self._b, gamma), pow(self._a, gamma))

    def to_sRGB(self):
        gamma = 1.0 / 0.45
        # return BGLColor(pow(self._r, gamma), pow(self._g, gamma), pow(self._b, gamma), self._a * 1.0)
        return BGLColor(pow(self._r, gamma), pow(self._g, gamma), pow(self._b, gamma), pow(self._a, gamma))

    @staticmethod
    def blended(color_a: "BGLColor", color_b: "BGLColor", blend_factor=0.5):
        blend_factor = clamp(blend_factor, 0.0, 1.0)
        new_color = BGLColor()
        # out = alpha * c1 + (1 - alpha) * c2
        blend_inv = 1 - blend_factor
        new_color.r = blend_factor * color_a.r + blend_inv * color_b.r
        new_color.g = blend_factor * color_a.g + blend_inv * color_b.g
        new_color.b = blend_factor * color_a.b + blend_inv * color_b.b
        new_color.a = blend_factor * color_a.a + blend_inv * color_b.a

        return new_color

    def __iter__(self):
        return iter((self._r, self._g, self._b, self._a))

    def __add__(self, other):
        return BGLColor(self.r + other.r, self.g + other.g, self.b + other.b, self.a + other.a)

    def __sub__(self, other):
        return BGLColor(self.r - other.r, self.g - other.g, self.b - other.b, self.a - other.a)

    def __pow__(self, power, modulo=None):
        return BGLColor(self.r ** power, self.g ** power, self.b ** power, self.a)

    def __repr__(self):
        return f"{type ( self ).__name__} ( {self.r}, {self.g}, {self.b}, {self.a} )"


class BGLImage:
    # Should not be instanciated manually

    def __init__(self, image_preview):
        width, height = image_preview.image_size
        self._texture_id = bgl.Buffer(bgl.GL_INT, 1)
        self.pixel_buffer = bgl.Buffer(bgl.GL_FLOAT, width * height * 4, list(image_preview.image_pixels_float))

        bgl.glGenTextures(1, self._texture_id)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self._texture_id[0])
        bgl.glTexImage2D(
            bgl.GL_TEXTURE_2D, 0, bgl.GL_RGB, width, height, 0, bgl.GL_RGBA, bgl.GL_FLOAT, self.pixel_buffer
        )

        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)

    def __del__(self):
        bgl.glDeleteTextures(1, self._texture_id)

    @property
    def texture_id(self):
        return self._texture_id[0]


class BGLBound:
    """
    Origin min min is at bottom left corner
    """

    def __init__(self, min_position=None, max_position=None):
        if min_position is None:
            self.min = BGLCoord()
        else:
            self.min = min_position

        if max_position is None:
            self.max = BGLCoord()
        else:
            self.max = max_position

    @property
    def width(self):
        return self.max.x - self.min.x

    @property
    def height(self):
        return self.max.y - self.min.y

    @property
    def center(self):
        return BGLCoord(self.min.x + self.width * 0.5, self.min.y + self.height * 0.5)

    @property
    def top_left(self):
        return BGLCoord(self.min.x, self.max.y)

    @property
    def top_mid(self):
        return BGLCoord(self.min.x + self.width * 0.5, self.max.y)

    @property
    def top_right(self):
        return BGLCoord(self.max.x, self.max.y)

    @property
    def mid_right(self):
        return BGLCoord(self.max.x, self.min.y + self.height * 0.5)

    @property
    def bottom_right(self):
        return BGLCoord(self.max.x, self.min.y)

    @property
    def bottom_mid(self):
        return BGLCoord(self.min.x + self.width * 0.5, self.min.y)

    @property
    def bottom_left(self):
        return BGLCoord(self.min.x, self.min.y)

    @property
    def mid_left(self):
        return BGLCoord(self.min.x, self.min.y + self.height * 0.5)

    def get_point(self, mode):
        """
            return the coordinates of the specified point of the boundary box
            mode can be: TOP_LEFT, TOP_MID, TOP_RIGHT, MID_RIGHT, BOTTOM_RIGHT, BOTTOM_MID, BOTTOM_LEFT, MID_LEFT, CENTER
        """
        if "TOP_LEFT" == mode:
            return self.top_left
        if "TOP_MID" == mode:
            return self.top_mid
        if "TOP_RIGHT" == mode:
            return self.top_right
        if "MID_RIGHT" == mode:
            return self.mid_right
        if "BOTTOM_RIGHT" == mode:
            return self.bottom_right
        if "BOTTOM_MID" == mode:
            return self.bottom_mid
        if "BOTTOM_LEFT" == mode:
            return self.bottom_left
        if "MID_LEFT" == mode:
            return self.mid_left
        if "CENTER" == mode:
            return self.center
        return

    def clamp(self, position: BGLCoord):
        return BGLCoord(clamp(position.x, self.min.x, self.max.x), clamp(position.y, self.min.y, self.max.y))

    def fully_contains(self, bound: "BGLBound"):
        """
        Check if the bound fully englobes the other bound.
        """
        if (
            self.min.x <= bound.min.x
            and self.min.y <= bound.min.y
            and self.max.x >= bound.max.x
            and self.max.y >= bound.max.y
        ):
            return True

        return False

    def do_overlap(self, bound: "BGLBound"):
        if self.min.x >= bound.max.x or bound.min.x >= self.max.x:
            return False

        # If one rectangle is above other
        if self.min.y >= bound.max.y or bound.min.y >= self.max.y:
            return False

        return True

    def __add__(self, other):
        return BGLBound(
            BGLCoord(min(self.min.x, other.min.x), min(self.min.y, other.min.y)),
            BGLCoord(max(self.max.x, other.max.x), max(self.max.y, other.max.y)),
        )

    def __iadd__(self, other):
        self.min.x = min(self.min.x, other.min.x)
        self.min.y = min(self.min.y, other.min.y)
        self.max.x = max(self.max.x, other.max.x)
        self.max.y = max(self.max.y, other.max.y)

        return self


class BGLImageManager:
    def __init__(self):
        self.pcoll = bpy.utils.previews.new()

    def load_image(self, path):
        p = Path(path)
        return BGLImage(self.pcoll.load(p.stem, str(p), "IMAGE"))

    def __del__(self):
        bpy.utils.previews.remove(self.pcoll)


class BGLTransform:
    def __init__(self):
        pass

    def apply_transform(self, region: "BGLRegion", position: BGLCoord, clip_to_region=True):
        return BGLCoord(position.x, position.y)


class BGLViewToRegion(BGLTransform):
    def __init__(self, apply_to_x=True, apply_to_y=True):
        BGLTransform.__init__(self)
        self.apply_to_x = apply_to_x
        self.apply_to_y = apply_to_y

    def apply_transform(self, region: "BGLRegion", position: BGLCoord, clip_to_region=True):
        new_pos = region.view_to_region(position, clip_to_region)
        if self.apply_to_x is False:
            new_pos.x = position.x

        if self.apply_to_y is False:
            new_pos.y = position.y

        return new_pos


class BGLRegion:
    def __init__(self, crop_left=0, crop_bottom=0, crop_right=0, crop_top=0):
        self._crops = (crop_left, crop_bottom, crop_right, crop_top)
        self.bl_region: bpy.types.Region = None
        self.transform = BGLTransform()

    @property
    def bound(self) -> BGLBound:
        return BGLBound(
            BGLCoord(self._crops[0], self._crops[1]),
            BGLCoord(self.bl_region.width - self._crops[2], self.bl_region.height - self._crops[3]),
        )

    def view_to_region(self, position: BGLCoord, region_clip=True) -> BGLCoord:
        if region_clip:
            position = clamp_to_region(position.x, position.y, self.bl_region, self.bound)
        return BGLCoord(*self.bl_region.view2d.view_to_region(*position))

    def mouse_to_region(self, position: BGLCoord()):
        return position - BGLCoord(self.bl_region.x, self.bl_region.y)


###
# Container types for properties
###


class BGLPropValue:
    """
    Data object which either encapsulate values as function or static value.
    Hence you can assign either non callable or callable objects.
    """

    def __init__(self, value):
        if isinstance(value, BGLPropValue):
            self._value = value._value
        else:
            self._value = value

    @property
    def value(self):
        if callable(self._value):
            return self._value()
        else:
            return self._value

    @value.setter
    def value(self, value):
        if isinstance(value, BGLPropValue):
            self._value = lambda o=value: o()
        else:
            self._value = value

    def __call__(self):
        return self.value


class BGLProp:
    """
    This is the class that should be used when providing public attributes on widgets.
    This a descriptor so attribute should be defined at class level.

    This forbid referencing the BGLPropValue to another.
    Assignment constructs a new BGLPropValue instance instead, also preventing type being changed.

    .. info::

            Advantages of the getter return BGLPropValue vs actual BGLPropValue.value
            + easy link of two property: a.prop = b.prop instead of a.prop = lambda o = b: b.prop
            + Can have special methods on BGLPropValue like operator overloading
            - need to manually query the value using either toto.value or toto(). Which can be confusing in some cases.

            currently switched to BGLPropValue.value way of doing.
    """

    def __init__(self, default_value=None):
        self._default_value = default_value

    def __set_name__(self, owner, name):
        self._name = name

    def __set__(self, obj, value):
        if not self._name in obj.__dict__:
            obj.__dict__[self._name] = BGLPropValue(None)
        obj.__dict__[self._name].value = value

    def __get__(self, obj, type=None) -> Any:
        if not self._name in obj.__dict__:
            self.__set__(obj, deepcopy(self._default_value))

        return obj.__dict__.get(self._name).value

