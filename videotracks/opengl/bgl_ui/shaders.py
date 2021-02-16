# -*- coding: utf-8 -*-
import gpu

_image_2d_fragment_shader = '''
    in vec2 texCoord_interp;
    out vec4 fragColor;
    uniform sampler2D image;

    void main()
    {
      fragColor = pow(texture(image, texCoord_interp), vec4(2.2));
    }

'''
UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")
IMAGE_SHADER_2D = gpu.types.GPUShader ( gpu.shader.code_from_builtin ( "2D_IMAGE" )[ "vertex_shader" ], _image_2d_fragment_shader )
