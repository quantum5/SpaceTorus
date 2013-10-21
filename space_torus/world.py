from bisect import bisect_left
from collections import OrderedDict
from operator import itemgetter
import hashlib
import os.path
import random

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
            background = info.get('background', False)

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
                    cloudmap_id = compile(sphere, radius + 2, int(radius / 2), int(radius / 2), cloud_texture,
                                          lighting=False)
                cheap, _, atm_texture = get_best_texture(atm_texture)
                if not cheap:
                    atmosphere_id = compile(disk, radius, radius + size, 30, atm_texture)

            world.tracker.append(Planet(planet_id, (x, y, z), (pitch, yaw, roll), delta=delta,
                                        atmosphere=atmosphere_id, cloudmap=cloudmap_id, background=background))
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
        world.generate_tori()
        return world


class World(object):
    def __init__(self):
        self.waypoints = []
        self.tracker = []
        self.tori = []
        self.x = None
        self.y = None
        self.z = None

    def generate_tori(self, iz=10):
        for w0, w1 in zip(self.waypoints[:-1], self.waypoints[1:]):
            x0, y0, z0 = w0
            x1, y1, z1 = w1
            dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
            tori = dz / iz
            ix = (dx + .0) / tori
            iy = (dy + .0) / tori
            x, y, z = w0

            for i in xrange(tori):
                dx = 2 + z / 15000
                dy = min(dx, z / 8000)
                self.tori.append((random.gauss(x, dx), random.gauss(y, dy)))
                x += ix
                y += iy
                z += iz
