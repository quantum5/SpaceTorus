from bisect import bisect_left
from collections import OrderedDict
from operator import itemgetter
import hashlib
import os.path

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except:
        print "No compatible JSON decoder found. Translation: you're fucked."

from space_torus.glgeom import *
from space_torus.entity import *
from space_torus.texture import *


TORUS_DISTANCE = 20
AU = TORUS_DISTANCE * 100


def get_best_texture(info, optional=False):
    cheap = False
    skip = False
    texture = None
    if isinstance(info, list):
        for item in info:
            if isinstance(item, list):
                if len(item) == 4:
                    cheap = True
                    texture = item
                    break
                continue
            try:
                texture = load_texture(item)
            except ValueError:
                pass
            else:
                break
    else:
        try:
            texture = load_texture(info)
        except ValueError:
            if optional:
                skip = True
            else:
                cheap = True
                texture = [1, 1, 1, 1]
    return cheap, skip, texture


def load_world(file):
    with open(os.path.join(os.path.dirname(__file__), file)) as f:
        world = World()
        root = json.load(f, object_pairs_hook=OrderedDict)

        e = lambda x: eval(str(x), {'__builtins__': None}, {'AU': AU})

        world.waypoints = []

        for waypoint in root['waypoints']:
            x, y, z = waypoint
            world.waypoints.append((e(x), e(y), e(z)))

        for planet in root['planets']:
            print "Loading %s." % planet
            info = root['planets'][planet]

            texture = info.get('texture', None)
            lighting = info.get('lighting', True)
            x = e(info.get('x', 0))
            y = e(info.get('y', 0))
            z = e(info.get('z', 0))
            pitch = e(info.get('pitch', 0))
            yaw = e(info.get('yaw', 0))
            roll = e(info.get('roll', 0))
            delta = e(info.get('delta', 5))
            radius = e(info.get('radius', None))

            cheap, skip, texture = get_best_texture(texture, optional=info.get('optional', False))
            if skip:
                continue
            if cheap:
                planet_id = compile(colourball, radius, int(radius / 2), int(radius / 2), texture)
            else:
                planet_id = compile(sphere, radius, int(radius / 2), int(radius / 2), texture, lighting=lighting)

            atmosphere_id = 0
            cloudmap_id = 0
            if 'atmosphere' in info:
                atmosphere_data = info['atmosphere']
                size = e(atmosphere_data.get('diffuse_size', None))
                atm_texture = atmosphere_data.get('diffuse_texture', None)
                cloud_texture = atmosphere_data.get('cloud_texture', None)
                cheap, _, cloud_texture = get_best_texture(cloud_texture)
                if not cheap:
                    cloudmap_id = compile(sphere, radius + 2, int(radius / 2), int(radius / 2), cloud_texture, lighting=False)
                cheap, _, atm_texture = get_best_texture(atm_texture)
                if not cheap:
                    atmosphere_id = compile(disk, radius, radius + size, 30, atm_texture)

            world.tracker.append(Planet(planet_id, (x, y, z), (pitch, yaw, roll), delta=delta, atmosphere=atmosphere_id, cloudmap=cloudmap_id))
            if 'ring' in info:
                ring_data = info['ring']
                texture = ring_data.get('texture', None)
                distance = e(ring_data.get('distance', radius * 1.2))
                size = e(ring_data.get('size', radius / 2))
                pitch = e(ring_data.get('pitch', pitch))
                yaw = e(ring_data.get('yaw', yaw))
                roll = e(ring_data.get('roll', roll))

                cheap, _, texture = get_best_texture(texture)
                if not cheap:
                    world.tracker.append(
                        Planet(compile(disk, distance, distance + size, 30, texture), (x, y, z),
                               (pitch, yaw, roll)))
        return world


class World(object):
    def __init__(self):
        self.waypoints = []
        self.tracker = []

    def torus_at(self, n):
        distance = TORUS_DISTANCE + .0

        zs = map(itemgetter(2), self.waypoints)
        index = bisect_left(zs, n * distance)
        if index < 1 or index > len(zs) - 2:
            return None
        w0, w1 = self.waypoints[index - 1:index + 1]

        x0, y0, z0 = w0
        x1, y1, z1 = w1

        dx, dy, dz = x1 - x0, y1 - y0, z1 - z0

        s = abs(dz / distance)
        dn = n - z0 / distance

        nx = x0 + (dx / s * dn)
        ny = y0 + (dy / s * dn)
        nz = z0 + (dz / s * dn)

        def r(n):
            # This makes me cry at how horribly beautiful it is
            return int(hashlib.md5(str(nz * n)).hexdigest()[-8:], 16) % 5

        nx += r(nx)
        ny += r(ny)

        return nx, ny, nz