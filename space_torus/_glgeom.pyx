from libc.math cimport sin, cos, sqrt
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy
cimport cython

include "_cyopengl.pxi"
cdef float PI = 3.1415926535897932324626
cdef float TWOPI = PI * 2

cdef extern from "Python.h":
    object PyBytes_FromStringAndSize(const char *s, Py_ssize_t len)
    const char* PyBytes_AsString(bytes o)

@cython.cdivision(True)
cpdef torus(float major_radius, float minor_radius, int n_major, int n_minor, tuple material, int shininess=125):
    '''
        Torus function from the OpenGL red book.
    '''
    glPushAttrib(GL_CURRENT_BIT)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [material[0], material[1], material[2], material[3]])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1, 1, 1, 1])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)

    assert n_major > 0 and n_minor > 0
    assert minor_radius > 0 and major_radius > 0

    cdef float major_s, minor_s
    major_s = TWOPI / n_major
    minor_s = TWOPI / n_minor

    cdef float a0, a1, x0, y0, x1, y1, b, c, r, z, m, x, y, z2
    cdef int i, j

    for i in xrange(n_major):
        a0 = i * major_s
        a1 = a0 + major_s
        x0 = cos(a0)
        y0 = sin(a0)
        x1 = cos(a1)
        y1 = sin(a1)

        glBegin(GL_TRIANGLE_STRIP)

        for j in xrange(n_minor + 1):
            b = j * minor_s
            c = cos(b)
            r = minor_radius * c + major_radius
            z = minor_radius * sin(b)

            x = x0 * c
            y = y0 * c
            z2 = z / minor_radius
            m = 1.0 / sqrt(x * x + y * y + z2 * z2)
            glNormal3f(x * m, y * z, z2 * m)
            glVertex3f(x0 * r, y0 * r, z)

            x = x1 * c
            y = y1 * c
            m = 1.0 / sqrt(x * x + y * y + z2 * z2)
            glNormal3f(x * m, y * z, z2 * m)
            glVertex3f(x1 * r, y1 * r, z)

        glEnd()
    glPopAttrib()

cpdef bytes bgr_to_rgb(bytes buffer, int width, int height, bint alpha=0, bint bottom_up=1):
    cdef int length = len(buffer)
    cdef int depth = length / (width * height)
    cdef int depth2 = depth - alpha
    cdef char *result = <char*>malloc(length)
    cdef const char *source = PyBytes_AsString(buffer)
    cdef int x, y, ioffset, ooffset, i, row = width * depth
    for y in xrange(height):
        for x in xrange(width):
            ioffset = y * width * depth + x * depth
            ooffset = (height - y - 1 if bottom_up else y) * row + x * depth
            for i in xrange(depth2):
                result[ooffset+i] = source[ioffset+depth2-i-1]
            if alpha:
                result[ooffset+depth2] = source[ioffset+depth2]
    cdef object final = PyBytes_FromStringAndSize(result, length)
    free(result)
    return final
