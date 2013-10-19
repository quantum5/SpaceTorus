from pyglet import image
from pyglet.gl import *
from ctypes import c_int, byref
import os.path
import struct

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

__all__ = ['load_texture']

id = 0
cache = {}

buf = c_int()
glGetIntegerv(GL_MAX_TEXTURE_SIZE, byref(buf))
max_texture = buf.value

power_of_two = gl_info.have_version(2) or gl_info.have_extension('GL_ARB_texture_non_power_of_two')

is_power2 = lambda num: num != 0 and ((num & (num - 1)) == 0)


def image_info(data):
    data = str(data)
    size = len(data)
    height = -1
    width = -1
    content_type = ''

    # handle GIFs
    if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
        # Check to see if content_type is correct
        content_type = 'image/gif'
        w, h = struct.unpack("<HH", data[6:10])
        width = int(w)
        height = int(h)

    # See PNG 2. Edition spec (http://www.w3.org/TR/PNG/)
    # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
    # and finally the 4-byte width, height
    elif ((size >= 24) and data.startswith('\211PNG\r\n\032\n')
          and (data[12:16] == 'IHDR')):
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[16:24])
        width = int(w)
        height = int(h)

    # Maybe this is for an older PNG version.
    elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
        # Check to see if we have the right content type
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[8:16])
        width = int(w)
        height = int(h)

    # handle JPEGs
    elif (size >= 2) and data.startswith('\377\330'):
        content_type = 'image/jpeg'
        jpeg = StringIO(data)
        jpeg.read(2)
        b = jpeg.read(1)
        try:
            while b and ord(b) != 0xDA:
                while ord(b) != 0xFF:
                    b = jpeg.read(1)
                while ord(b) == 0xFF:
                    b = jpeg.read(1)
                if 0xC0 <= ord(b) <= 0xC3:
                    jpeg.read(3)
                    h, w = struct.unpack(">HH", jpeg.read(4))
                    break
                else:
                    jpeg.read(int(struct.unpack(">H", jpeg.read(2))[0])-2)
                b = jpeg.read(1)
            width = int(w)
            height = int(h)
        except struct.error:
            pass
        except ValueError:
            pass

    return content_type, width, height


def check_size(width, height):
    if width > max_texture or height > max_texture:
        raise ValueError('Texture too large')
    elif not power_of_two:
        if not is_power2(width) or not is_power2(height):
            raise ValueError('Texture not power of two')


def load_texture(file, safe=False):
    global id, cache
    if file in cache:
        return cache[file]
    id += 1
    print "Loading image %s..." % file

    path = os.path.join(os.path.dirname(__file__), "assets", "textures", file)

    try:
        file = open(path, 'rb')
    except IOError:
        raise ValueError('Texture exists not')
    type, width, height = image_info(file.read(8192))
    file.seek(0, 0)
    if type:
        check_size(width, height)

    try:
        raw = image.load(path, file=file)
    except IOError:
        raise ValueError('Texture exists not')

    width, height = raw.width, raw.height
    check_size(width, height)

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