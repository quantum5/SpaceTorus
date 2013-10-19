from pyglet import image
from pyglet.gl import *
from ctypes import c_int, byref
import os.path

__all__ = ['load_texture']

id = 0
cache = {}

buf = c_int()
glGetIntegerv(GL_MAX_TEXTURE_SIZE, byref(buf))
max_texture = buf.value

power_of_two = gl_info.have_version(2) or gl_info.have_extension('GL_ARB_texture_non_power_of_two')

is_power2 = lambda num: num != 0 and ((num & (num - 1)) == 0)


def load_texture(file, safe=False):
    global id, cache
    if file in cache:
        return cache[file]
    id += 1
    print "Loading image %s..." % file


    try:
        raw = image.load(os.path.join(os.path.dirname(__file__), "assets", "textures", file))
    except IOError:
        raise ValueError('Texture exists not')


    width, height = raw.width, raw.height
    if width > max_texture or height > max_texture:
        raise ValueError('Texture too large')
    elif not power_of_two:
        if not is_power2(width) or not is_power2(height):
            raise ValueError('Texture not power of two')

    mode = GL_RGBA if 'A' in raw.format else GL_RGB
    # Flip from BGR to RGB
    # I hate you too, Pyglet...
    # REGULAR EXPRESSIONS ARE NOT MEANT TO PARSE BINARY DATA!!!
    texture = raw.get_data('RGBA', width * 4) if safe else raw.data[::-1] if 'BGR' in raw.format else raw.data

    buffer = [id] # Buffer to hold the returned texture id
    glGenTextures(1, (GLuint * len(buffer))(*buffer))

    glBindTexture(GL_TEXTURE_2D, buffer[0])

    #Load textures with no filtering. Filtering generally makes the texture blur.
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, mode, width, height, 0, mode, GL_UNSIGNED_BYTE, texture)

    cache[file] = buffer[0]

    return buffer[0]