# -*- coding: utf-8 -*-
import bgl, gpu
from gpu_extras.batch import batch_for_shader

from .types import BGLColor, BGLImage


class BGLShader:
    _shader = None
    vertex_shader = ""
    fragment_shader = ""

    def __enter__(self):
        self._build()
        self._shader.bind()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        gpu.shader.unbind()

    @classmethod
    def create_batch(cls, draw_mode, vertex_data, indices=None):
        cls._build()
        return batch_for_shader(cls._shader, draw_mode, vertex_data, indices=indices)

    @classmethod
    def draw_batch(cls, batch, blending=True):
        cls._build()
        if blending:
            bgl.glEnable(bgl.GL_BLEND)
        batch.draw(cls._shader)
        if blending:
            bgl.glDisable(bgl.GL_BLEND)

    @classmethod
    def _build(cls):
        if cls._shader is None:
            cls._shader = gpu.types.GPUShader(cls.vertex_shader, cls.fragment_shader)


class BGLUniformShader(BGLShader):
    vertex_shader = gpu.shader.code_from_builtin("2D_UNIFORM_COLOR")["vertex_shader"]
    fragment_shader = gpu.shader.code_from_builtin("2D_UNIFORM_COLOR")["fragment_shader"]

    def set_color(self, color: BGLColor):
        self._shader.uniform_float(
            "color", color ** 0.454545
        )  # We'll do conversion here because fragment shader is a bit strange.


class BGLImageShader(BGLShader):
    vertex_shader = gpu.shader.code_from_builtin("2D_IMAGE")["vertex_shader"]
    fragment_shader = """
    in vec2 texCoord_interp;
    out vec4 fragColor;
    uniform sampler2D image;

    void main()
    {
      fragColor = pow(texture(image, texCoord_interp), vec4(2.2));
    }

"""

    def set_image(self, image: BGLImage):
        bgl.glActiveTexture(bgl.GL_TEXTURE0)  # see if we need to deactivate or not
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.texture_id)
        self._shader.uniform_int("image", 0)

